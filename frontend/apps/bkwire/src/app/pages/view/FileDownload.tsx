import { Close } from '@mui/icons-material';
import { Box, IconButton, Typography } from '@mui/material';
import React, { useImperativeHandle, useRef } from 'react';
import { useCallback, useState } from 'react';
import { FileDownloadLink, FileDownloadRoot } from './FileDownload.styled';
import {
  DocketFile,
  DocketFileTypes,
  UserFileAccess,
} from '../../api/api.types';
import {
  useGetDocketFiles,
  useGetUserFileAccess,
  useGetViewer,
} from '../../api/api.hooks';
import { Loading } from '../../components/loading/Loading';
import useApi from '../../api/api.client';
import { useQueryClient } from 'react-query';

export type FileDownloadHandle = {
  open: (
    caseId?: number,
    docketId?: number,
    docUrl?: string,
    docsCount?: number,
    fileType?: DocketFileTypes
  ) => void;
  close: () => void;
};

export const FileDownload = React.forwardRef<FileDownloadHandle, unknown>(
  (_, ref) => {
    const [isModalOpen, setModalOpen] = useState(false);

    const caseIdRef = useRef<number>();
    const docketIdRef = useRef<number>();
    const docUrlRef = useRef<string>();
    const docsCountRef = useRef<number>();
    const fileTypeRef = useRef<DocketFileTypes>();

    const { data: viewer } = useGetViewer();

    const {
      data: files,
      refetch: refetchFiles,
      isRefetching: isRefetchingFiles,
      isLoading: isLoadingFiles,
    } = useGetDocketFiles(
      caseIdRef.current,
      docketIdRef.current,
      docUrlRef.current,
      docsCountRef.current
    );

    const {
      data: fileAccess,
      refetch: refetchFileAccess,
      isRefetching: isRefetchingFileAccess,
      isLoading: isLoadingFileAccess,
    } = useGetUserFileAccess(caseIdRef.current);

    const open = useCallback(
      (
        caseId?: number,
        docketId?: number,
        docUrl?: string,
        docsCount = 0,
        fileType = 'other'
      ) => {
        caseIdRef.current = caseId;
        docketIdRef.current = docketId;
        docUrlRef.current = docUrl;
        docsCountRef.current = docsCount;
        fileTypeRef.current = fileType;

        setTimeout(() => {
          if (docketId && docsCount > 1) {
            refetchFiles();
          }
          refetchFileAccess();
        }, 0);
        setModalOpen(true);
      },
      [refetchFiles, refetchFileAccess]
    );

    const close = useCallback(() => {
      caseIdRef.current = undefined;
      docketIdRef.current = undefined;
      docUrlRef.current = undefined;
      docsCountRef.current = undefined;
      fileTypeRef.current = undefined;

      setModalOpen(false);
    }, [setModalOpen]);

    useImperativeHandle(
      ref,
      () => ({
        open,
        close,
      }),
      [open, close]
    );

    const { get } = useApi();
    const queryClient = useQueryClient();
    const [downloadingLink, setDownloadingLink] = useState<string | null>(null);

    const download = useCallback(
      async (fileLink: string) => {
        if (downloadingLink === null && caseIdRef.current && fileLink) {
          setDownloadingLink(fileLink);
          try {
            const { data: url } = await get<string>('/file-link-download', {
              params: {
                dci_id: caseIdRef.current,
                doc_url: fileLink,
              },
            });

            if (url !== 'File Download Failed') {
              window.open(url, '_blank');
            }
          } catch {
            console.log('Something went wrong! Try again later.');
          } finally {
            setDownloadingLink(null);
            refetchFileAccess();
            queryClient.invalidateQueries('query-viewer'); // for file_download_count
          }
        }
      },
      [downloadingLink, get, queryClient, refetchFileAccess]
    );

    const hasAccess = useCallback(
      (f: DocketFile) => {
        return (
          fileTypeRef.current === 'petition' ||
          fileTypeRef.current === 'creditors' ||
          (fileAccess || []).filter(
            (a: UserFileAccess) =>
              (!docketIdRef.current ||
                a.docket_entry_id === docketIdRef.current) &&
              a.docket_entry_link === f.link
          ).length > 0
        );
      },
      [fileAccess]
    );

    return (
      <FileDownloadRoot open={isModalOpen} onClose={close}>
        <IconButton className="modal-close" onClick={close}>
          <Close />
        </IconButton>
        <Box display="flex" flexDirection="column">
          <Box className="modal-header">
            <Typography variant="h2" py={2} fontSize="1.75rem">
              {docketIdRef.current
                ? 'Files available for download'
                : 'My Files'}
            </Typography>
          </Box>
          <Box className="modal-body">
            {isLoadingFiles ||
            isRefetchingFiles ||
            isLoadingFileAccess ||
            isRefetchingFileAccess ? (
              <Loading />
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>
                      {docketIdRef.current || fileAccess?.length
                        ? 'File name'
                        : "You haven't downloaded any files for this case yet."}
                    </th>
                    <th>{docketIdRef.current ? 'File access' : ''}</th>
                  </tr>
                </thead>
                {docketIdRef.current ? (
                  <tbody>
                    {(files ?? []).map((f) => (
                      <tr key={f.link}>
                        <td>
                          <FileDownloadLink
                            onClick={() => download(f.link)}
                            disabled={downloadingLink !== null}
                          >
                            {f.filename}
                          </FileDownloadLink>
                        </td>
                        <td>
                          {downloadingLink === f.link ? (
                            <Loading size={16} />
                          ) : (
                            <span
                              className={`file-access ${
                                hasAccess(f) ? 'owned' : 'not-owned'
                              }`}
                            />
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                ) : (
                  <tbody>
                    {(fileAccess || []).map((f) => (
                      <tr key={f.docket_entry_link}>
                        <td>
                          <FileDownloadLink
                            onClick={() => download(f.docket_entry_link)}
                            disabled={downloadingLink !== null}
                          >
                            {f.docket_entry_name}
                          </FileDownloadLink>
                        </td>
                        <td>
                          {downloadingLink === f.docket_entry_link && (
                            <Loading size={16} />
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                )}
              </table>
            )}
          </Box>
          {viewer && (
            <Box className="modal-footer">
              {docketIdRef.current
                ? `${
                    viewer.file_download_max - viewer.file_download_count
                  } remaining downloads`
                : fileAccess?.length
                ? 'You can download these files at any time'
                : ''}
            </Box>
          )}
        </Box>
      </FileDownloadRoot>
    );
  }
);
