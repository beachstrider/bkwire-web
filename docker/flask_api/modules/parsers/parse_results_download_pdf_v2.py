#!/usr/bin/python
# -*- coding: latin-1 -*-
from pyparsing import (
    makeHTMLTags,
    commonHTMLEntity,
    replaceHTMLEntity,
    htmlComment,
    anyOpenTag,
    anyCloseTag,
    LineEnd,
    replaceWith,
)
import copy
import re
import os
import sys
import pprint
import pyparsing
from os import path
import urllib.request
import logging.config
from logtail import LogtailHandler
import lxml.html as lh
import pandas as pd
from lxml import etree
import xml.etree.ElementTree as ET
from time import strptime
from bs4 import BeautifulSoup
from datetime import date, timedelta

### MODULE SETUP ###
sys.path.insert(0, '/app')
from modules.aws.check_s3_objects import check_against_s3_objects, download_pdf_from_s3_archive
from modules.address.international_parser import IntAddyParse

### LOGGING SETUP ###
handler = LogtailHandler(source_token=os.environ['LOG_SOURCE_TOKEN'])
#log_file_path = path.join(path.dirname(path.abspath(__file__)), '/app/logging/logging.ini')
#logging.config.fileConfig(log_file_path)
#logger = logging.getLogger(__name__)
#logger_list = ['boto', 'boto3', 'chardet', 'urllib3', 'botocore', 's3transfer', 'PIL']
#for i in logger_list:
#    logging.getLogger(i).setLevel(logging.CRITICAL) #sets all #logging sources to crit level

logger = logging.getLogger(__name__)
logger.handlers = []
logger.setLevel(logging.DEBUG) # Set minimal log level
logger.addHandler(handler) # asign handler to logger

# Setup globals
xmlDict = {}
pdf_dl_pages = []
html_table_dic = {}
pp = pprint.PrettyPrinter(indent=4)
today = date.today().strftime('%m/%d/%Y')
class ResultsParserSvc:
    def __init__(self, pls):
        logger.info('Init results parser')
        self.pacer_login_session = pls

    def address_parser(self, addy):
        logger.debug('Address to parse: ' + addy)
        iap = IntAddyParse()
        company_name = None
        company_city = None
        company_state = None
        company_zip = None

        try:
            adr = iap.parse_address(addy)
        except Exception as e:
            logger.warning(f"unable to successfully parse addy: {e}")

        try:
            company_name = adr[0]
        except:
            pass
        try:
            company_city = adr[4]
        except:
            pass
        try:
            company_state = adr[2]
        except:
            pass
        try:
            company_zip = adr[3]
        except:
            pass

        return(company_name, company_city, company_state, company_zip)


    def parse_html_table_to_dic(self, k, soup):
        """Parse HTML Table - Build data object from the results of that HTML table
        We use a screen scrape method to pull data from HTML forms and parse those
        into Objects we store and utilize to download PDF files that we need for
        parsing

        :param k: Case name used as KEY for dictionary
        :param soup: This is HTML form data that we parse for objects we need
        :return: We return the dictionary we build back to MAIN script for logic
        """
        logger.info(f'Parsing HTML table to Dictionary: {k}')

        a_href_link = {}
        html_table_dic[k] = {}
        tax_id_ein = None
        html_table_dic[k]['tax_id_ein'] = None
        html_table_dic[k]['debtor_name'] = None
        html_table_dic[k]['debtor_address'] = None
        #html_table_dic[k]['docket_table'] = None

        html_table_list = []
        my_dke_to_append = []
        docket_table_list = []
        my_test_list_results = []

        #Regex for TAXID
        regex_tax_id  = r"Tax ID \/ EIN: (\d+-\d+)"
        #Regex for Debtor Information
        regex_debtor_info = r"Debtor\d?\d?(?s)(.+[A-Z]{2} [0-9]{5}).+Tax ID"
        regex_debtor_info_nid = r"Debtor\d?\d?(?s)(.+?[A-Z]{2} [0-9]{5})"
        #Regex for Docket Entries
        regex_docket_entries = r"^[0-9]{2}\/[0-9]{2}\/[0-9]{4}(.+)"
        num_table_we_want = r"Docket Text"

        docket_table = None
        table_count = 0
        tables = soup.find_all('table')
        try:
            while(len(tables) > table_count): # Loop through all html tables
                for row in tables[table_count].find_all('tr'): # Find all <tr> tags and loop over them
                    rdi = re.search(regex_debtor_info, row.text)
                    rdi_nid = re.search(regex_debtor_info_nid, row.text)
                    # If we find regex matches from above add to list
                    if rdi:
                        html_table_list = rdi.group(1).split('\n')

                    if rdi_nid:
                        html_table_list = rdi_nid.group(1).split('\n')

                    rti = re.search(regex_tax_id, row.text)
                    if rti:
                        tax_id_ein = rti.group(1)

                    rdt = re.search(regex_docket_entries, row.text)
                    if rdt:
                        docket_table_list.append(str(rdt.group(1)))

                    rdn = re.search(num_table_we_want, row.text)
                    if rdn:
                        docket_table = tables[table_count]

                # Build debtor address from findings with a little join foo
                debtor_address = ' '.join([str(elem) for elem in html_table_list[1:]])
                logger.debug('debtor_addy: ' + debtor_address)
                # Increment table count
                table_count += 1
            # remove last random string
            if len(docket_table_list) > 0:
                docket_table_list.pop()
            else:
                logger.debug("docket_table_list=0")
        except Exception as e:
            logger.error(f'Parsing HTML tables to Dict FAILED: {e}')

        try: # Lets build a data object with all our things
            html_table_dic[k]['tax_id_ein'] = tax_id_ein
            html_table_dic[k]['debtor_name'] = html_table_list[0]
            html_table_dic[k]['debtor_address'] = debtor_address
            html_table_dic[k]['docket_table'] = docket_table
        except Exception as e:
            logger.info('Debtor additional info was NULL')
            logger.debug(k)
            logger.error(e)

        # clear tables for next case in loop
        a_href_link = {}
        docket_table_list = []

        #logger.debug(html_table_dic)
        self.soup_to_html_dic = html_table_dic
        return(html_table_dic)

    def parse_docket_entries(self, html_tables_results, pacer_data_results, pacer_pdf_results):
        html_table_key_list = ['tax_id_ein', 'debtor_name', 'debtor_address', 'docket_table']
        for key,val in html_tables_results.items():
            pacer_pdf_results[key] = {}
            pdf_doc_files = []
            pacer_data_results[key]['pdf_dl_skip'] = False
            pacer_data_results[key]['pdf_dl_status_201'] = None
            pacer_data_results[key]['pdf_dl_status_204206'] = None
            modified_case_number = pacer_data_results[key]['case_number'].split(':')
            modified_case_link   = pacer_data_results[key]['case_link'].split('/cgi-bin')
            referer_url          = pacer_data_results[key]['case_link'].replace('iqquerymenu.pl','DktRpt.pl')
            pdf_file_name        = pacer_data_results[key]['court_id'] +'.'+ modified_case_number[1]
            pacer_data_results[key]['company_address'] = None
            pacer_data_results[key]['company_city'] = None
            pacer_data_results[key]['company_state'] = None
            pacer_data_results[key]['company_zip'] = None
            pacer_data_results[key]['company_industry'] = None
            pacer_data_results[key]['sub_chapv'] = False

            iap = IntAddyParse()
            if html_tables_results[key]['debtor_address']:
                logger.debug('HTML_TABLE_RESULTS(debtor_address): ' + str(html_tables_results[key]['debtor_address']))
                try:
                    adr = iap.parse_address(html_tables_results[key]['debtor_address'])
                except Exception as e:
                    pacer_data_results[key]['company_address'] = None
                    pacer_data_results[key]['company_city'] = None
                    pacer_data_results[key]['company_state'] = None
                    pacer_data_results[key]['company_zip'] = None
                    pacer_data_results[key]['company_industry'] = None
                    logger.error(e)
                try:
                    pacer_data_results[key]['company_city'] = adr[4]
                except:
                    pacer_data_results[key]['company_city'] = None
                try:
                    pacer_data_results[key]['company_state'] = adr[2]
                except:
                    pacer_data_results[key]['company_state'] = None
                try:
                    pacer_data_results[key]['company_zip'] = adr[3]
                except:
                    pacer_data_results[key]['company_zip'] = None
                try:
                    pacer_data_results[key]['company_industry'] = 'Unknown'
                except:
                    pacer_data_results[key]['company_industry'] = None
                try:
                    pacer_data_results[key]['company_address'] = adr[1] + ' ' + adr[5]
                except:
                    pacer_data_results[key]['company_address'] = html_tables_results[key]['debtor_address']
            else:
                pacer_data_results[key]['company_address'] = None
                pacer_data_results[key]['company_city'] = None
                pacer_data_results[key]['company_state'] = None
                pacer_data_results[key]['company_zip'] = None
                pacer_data_results[key]['company_industry'] = None

            try:
                docket_table_list = copy.copy(pacer_data_results[key]['docket_table'])
                petition_entry = docket_table_list.pop(0)
                if re.search('Petition for Individuals', petition_entry, re.I):
                    logger.debug(f"Skipping petition for individuals: {key}")
                    del pacer_data_results[key]
                    pass
                elif re.search('Individual Chapter 11 Voluntary Petition', petition_entry):
                    logger.debug(f"Skipping petition for individuals: {key}")
                    del pacer_data_results[key]
                    pass
                elif re.search('Voluntary Petition Individual', petition_entry):#Chapter 11 Voluntary Petition for Individual
                    logger.debug(f"Skipping petition for individuals: {key}")
                    del pacer_data_results[key]
                    pass
                elif re.search('Chapter 11 Voluntary Petition for Individual', petition_entry):
                    logger.debug(f"Skipping petition for individuals: {key}")
                    del pacer_data_results[key]
                    pass                                      
                else:
                    logger.info(f"found petition entry: {petition_entry}")
                    if re.search('Subchapter V', petition_entry, re.I): #Subchapter V
                        logging.debug(f"found subchapter v case: {key}")
                        pacer_data_results[key]['sub_chapv'] = True                    
                    split_case_link = pacer_data_results[key]['case_link'].split('?')
                    docket_entry_parse_url = petition_entry.split(':bkwsplit:')                    
                    chop_it_up = docket_entry_parse_url[1].split('/doc1/')
                    pdf_file_name_full_wpage = f"{pdf_file_name}.{split_case_link[1]}.{chop_it_up[1]}-petition.pdf"
                    pdf_file_type = 'petition'
                    pacer_pdf_results[key][pdf_file_name_full_wpage] = False
                    check_s3_exists = check_against_s3_objects(pdf_file_name_full_wpage, referer_url)
                    if check_s3_exists == False:
                        logger.info('NO S3 object exists in archive')                        
                        self.download_pdf_href(docket_entry_parse_url[1], referer_url, pdf_file_name_full_wpage, pacer_data_results, key, pacer_pdf_results)
                        #pdf_doc_files.append({'filename': pdf_file_name_full_wpage, 'link': docket_entry_parse_url[1]})
                        # TODO: New module that just hits the endpoint with a post and returns the dl'd object
                    else:
                        logger.info('S3 exists in archive')
                        results = download_pdf_from_s3_archive(pdf_file_name_full_wpage, referer_url)
                        if results != False:
                            pacer_data_results[key]['pdf_dl_status_201'] = 'complete'
                            pacer_pdf_results[key][pdf_file_name_full_wpage] = True
                            logger.info('Download from S3 archive SUCCESS')
                        else:
                            pacer_data_results[key]['pdf_dl_status_201'] = 'incomplete'
                            logger.info('Download from S3 archive FAILED')
                            logger.error(results)
                    pdf_doc_files.append({'filename': pdf_file_name_full_wpage, 'link': docket_entry_parse_url[1], 'type': pdf_file_type})
                    pacer_data_results[key]['pdf_doc_files'] = pdf_doc_files                            
            except Exception as e:
                logger.warning(f"Petition parsing failed: {e}")

            try:
                docket_table_list = copy.copy(pacer_data_results[key]['docket_table'])
                petition_entry = docket_table_list.pop(0)
                count = 0
                for l in docket_table_list:
                    split_case_link = pacer_data_results[key]['case_link'].split('?')
                    if re.search('Unsecured', l):
                        if re.search('Not Timely Filed', l, re.I):
                            pass
                        else:
                            logger.info(f"found unsecured entry: {l}")
                            docket_entry_parse_url = l.split(':bkwsplit:')
                            chop_it_up = docket_entry_parse_url[1].split('/doc1/')
                            #pdf_file_name_full_wpage = f"{pdf_file_name}.{split_case_link[1]}.{chop_it_up[0]}-petition.pdf"                            
                            pdf_file_name_full_wpage = f"{pdf_file_name}.{split_case_link[1]}.{chop_it_up[1]}-creditors.pdf"
                            pdf_file_type = 'creditors'
                            pacer_pdf_results[key][pdf_file_name_full_wpage] = False                    
                            check_s3_exists = check_against_s3_objects(pdf_file_name_full_wpage, referer_url)
                            count += 1
                            if check_s3_exists == False:
                                logger.info('NO S3 object exists in archive')
                                #this goes back to import, trigger download and perform logic below for results
                                self.download_pdf_href(docket_entry_parse_url[1], referer_url, pdf_file_name_full_wpage, pacer_data_results, key, pacer_pdf_results)                            
                            else:
                                logger.info('S3 exists in archive')
                                results = download_pdf_from_s3_archive(pdf_file_name_full_wpage, referer_url)
                                if results != False:
                                    pacer_data_results[key]['pdf_dl_status_204206'] = 'complete'
                                    pacer_pdf_results[key][pdf_file_name_full_wpage] = True
                                    logger.info('Download from S3 archive SUCCESS')
                                else:
                                    pacer_data_results[key]['pdf_dl_status_204206'] = 'incomplete'
                                    logger.info('Download from S3 archive FAILED')
                                    logger.error(results)
                            pdf_doc_files.append({'filename': pdf_file_name_full_wpage, 'link': docket_entry_parse_url[1], 'type': pdf_file_type})
                            pacer_data_results[key]['pdf_doc_files'] = pdf_doc_files                                          
            except Exception as e:
                logger.warning(f"Pacer docket parse fail: {e}")
                pass
        return(pacer_data_results, pacer_pdf_results)

    def download_pdf_href(self, href_link, case_link, pdf_fn, pacer_data_results, key, pacer_pdf_results):
        """
        Attempt several stratgies to get PDF content from PACER
        1 - POST to the PDF URL
        2 - Payload sends back more HTML - we follow temp link for download
        3 - PDF content is in the HTML response and we strip non pdf chars and save
        """
        # Parse Vars
        response = None
        pdf_dl_dir = 'results/'
        split_case_link = case_link.split('?')
        split_case_link_slash = case_link.split('/')
        header_params = {'content-type':'application/x-www-form-urlencoded','referer':href_link}
        dl_pdf_data = {'caseid': split_case_link[1], 'got_receipt': 1, 'pdf_header': 1}
        # PDF Vars
        pdf_file_name = pdf_fn
        pdf_full_path_wname = pdf_dl_dir + pdf_file_name
        logger.info('Running POST: ' + href_link + ' caseID: ' + split_case_link[1])

        try: #Using all our parsing to this point - attempt to Download PDF
            response = self.pacer_login_session.post(href_link, headers=header_params, data=dl_pdf_data, timeout=20, allow_redirects=True)
            logger.debug('response: ' + str(response))
        except Exception as e:
            logger.info('PDF POST Request FAILED! ' + href_link)
            logger.error(e)
        # Check response for PDF content
        if response != None:
            pdf_content = re.search(r"%PDF", response.text)
            if pdf_content:
                pdf_contents = self.scrub_html_from_content(response)
                self.pdf_from_content(pdf_contents, pdf_full_path_wname, pacer_data_results, key, pacer_pdf_results, pdf_file_name)
            # if our results were more HTML - follow link to download PDF from temp URL
            elif response != None and response.headers['content-type'] == 'text/html; charset=UTF-8':
                self.download_pdf_from_temp_url(response, case_link, pdf_full_path_wname, pdf_fn, pacer_data_results, key, pacer_pdf_results)
            # if the response was actual PDF bytes - parse the pdf content
            elif response != None and response.headers['content-type'] == 'application/pdf':
                self.pdf_from_content(response, pdf_full_path_wname, pacer_data_results, key, pacer_pdf_results, pdf_file_name)
            else:
                logger.info('FAILED: Response is None or Unknown type' + str(href_link))
        else:
            logger.info('Request response was False')
            pass


    def download_pdf_files(self, file_link, file_w_path, doc_url_split):
        """
        Attempt several stratgies to get PDF content from PACER
        1 - POST to the PDF URL
        2 - Payload sends back more HTML - we follow temp link for download
        3 - PDF content is in the HTML response and we strip non pdf chars and save
        """
        # Parse Vars
        response = None
        header_params = {'content-type':'application/x-www-form-urlencoded','referer':file_link}
        dl_pdf_data = {'got_receipt': 1, 'pdf_header': 1}

        try: #Using all our parsing to this point - attempt to Download PDF
            response = self.pacer_login_session.post(file_link, headers=header_params, data=dl_pdf_data, timeout=20, allow_redirects=True)
            logger.debug('response: ' + str(response))
        except Exception as e:
            logger.info('PDF POST Request FAILED! ' + file_link)
            logger.error(e)
            return 'File Download Failed'
        # Check response for PDF content
        if response != None:
            pdf_content = re.search(r"%PDF", response.text)
            if pdf_content:
                pdf_contents = self.scrub_html_from_content(response)
                self.pdf_from_content_no_opt(pdf_contents, file_w_path)
            # if our results were more HTML - follow link to download PDF from temp URL
            elif response != None and response.headers['content-type'] == 'text/html; charset=UTF-8':
                self.download_pdf_from_temp_url_no_opt(response, file_w_path, doc_url_split)
            # if the response was actual PDF bytes - parse the pdf content
            elif response != None and response.headers['content-type'] == 'application/pdf':
                self.pdf_from_content_no_opt(response, file_w_path)
            else:
                logger.info('FAILED: Response is None or Unknown type' + str(file_link))
                return 'File Download Failed'
        else:
            logger.info('Request response was False')
            return 'File Download Failed'
        return 'File Download Success'

    def scrub_html_from_content(self, r):
        """
        This function will strip non PDF elements from response payload
        """
        pdf_elements = b"(%PDF.+(?s).+%%EOF)"
        rdi = re.search(pdf_elements, r.content)
        if rdi:
            return(rdi.group(0))
        else:
            return(r)

    def download_pdf_from_temp_url(self, r, case_link, pdf_full_path_wname, pdf_fn, pacer_data_results, key, pacer_pdf_results):
        pdf_temp_url = None
        pdf_doc_files = []
        pacer_data_results[key]['pdf_filename'] = None
        split_case_link_slash = case_link.split('/')

        soup = BeautifulSoup(r.content, 'lxml')
        tags = soup.find_all('a')
        for t in tags:
            try:
                s = re.search(r"(.+show_temp.+)", str(t.attrs['href']))
                v = re.search(r"doc1", str(t.attrs['href']))
                if s:
                    pdf_temp_url = 'https://' + split_case_link_slash[2] + s.group(0)
                    try:
                        logger.info('Running POST(download) from temp_url: ' + pdf_temp_url)
                        urllib.request.urlretrieve(pdf_temp_url, pdf_full_path_wname)
                        if re.search('petition',pdf_full_path_wname):
                            pacer_data_results[key]['pdf_dl_status_201'] = 'complete'
                            pacer_data_results[key]['pdf_filename_201'] = pdf_fn
                            #pdf_doc_files.append({'filename': pdf_full_path_wname, 'link': docket_entry_parse_url[1]})
                            #pacer_data_results[key]['pdf_doc_files'] = pdf_doc_files
                        else:
                            pacer_data_results[key]['pdf_dl_status_204206'] = 'complete'
                            pacer_data_results[key]['pdf_filename_204206'] = pdf_fn
                            #pdf_doc_files.append(pdf_fn)
                            #pacer_data_results[key]['pdf_doc_files'] = pdf_doc_files                            
                    except Exception as e:
                        logger.warning(f'FAILED: Unable to download PDF: {pdf_temp_url} : {e}')
                elif v:
                    if t.text == '1':
                        pdf_nested_href = 'https://' + split_case_link_slash[2] + t.attrs['href']
                        logger.info('Running POST(download) from temp_url: ' + pdf_nested_href)
                        self.download_pdf_href(pdf_nested_href, case_link, pdf_fn, pacer_data_results, key, pacer_pdf_results)
                else:
                    pass
            except Exception as e:
                logger.warning(f'temp_url download failed: {e}, trying something else..')
                pass

    def pdf_from_content(self, r, path_file_name, pacer_data_results, key, pacer_pdf_results, file_name):
        logger.info('Downloading PDF from content response')
        pdf_doc_files = []
        pacer_data_results[key]['pdf_filename'] = None
        #logger.info(r.text)
        try:
            with open(path_file_name, 'wb') as f:
                f.write(r)
            f.close()
            if re.search('petition',file_name):
                pacer_data_results[key]['pdf_dl_status_201'] = 'complete'
                pacer_data_results[key]['pdf_filename_201'] = file_name
               # pdf_doc_files.append(file_name)
               # pacer_data_results[key]['pdf_doc_files'] = pdf_doc_files                
            else:
                pacer_data_results[key]['pdf_dl_status_204206'] = 'complete'
                pacer_data_results[key]['pdf_filename_204206'] = file_name
               # pdf_doc_files.append(file_name)
               # pacer_data_results[key]['pdf_doc_files'] = pdf_doc_files 
        except Exception as e:
            logger.info('Downloading PDF from content FAILED')
            logger.error(e)


    def download_pdf_from_temp_url_no_opt(self, contents, file_w_path, doc_url_split):
        pdf_temp_url = None
        
        soup = BeautifulSoup(contents.content, 'lxml')
        tags = soup.find_all('a')
        for t in tags:
            try:
                s = re.search(r"(.+show_temp.+)", str(t.attrs['href']))
                v = re.search(r"doc1", str(t.attrs['href']))
                if s:
                    pdf_temp_url = f"{doc_url_split}{s.group(0)}"
                    try:
                        logger.info('Running (download) from temp_url: ' + pdf_temp_url)
                        urllib.request.urlretrieve(pdf_temp_url, file_w_path)                       
                    except Exception as e:
                        logger.warning(f'FAILED: Unable to download PDF: {pdf_temp_url} : {e}')
                        return 'File Download Failed'
                elif v:
                    if t.text == '1':
                        pdf_nested_href = f"{doc_url_split}{t.attrs['href']}"
                        logger.info('Running POST(download) from temp_url: ' + pdf_nested_href)
                        self.download_pdf_files(pdf_nested_href, file_w_path, doc_url_split)
                else:
                    pass
            except Exception as e:
                logger.warning(f'temp_url download failed: {e}, trying something else..')
                pass

    def pdf_from_content_no_opt(self, r, path_file_name):
        logger.info('Downloading PDF from content response')
        #logger.info(r.text)
        try:
            with open(path_file_name, 'wb') as f:
                f.write(r)
            f.close()
        except Exception as e:
            logger.info('Downloading PDF from content FAILED')
            logger.error(e)
            return 'File Download Failed'

    def docket_table_parse(self, docket_table_data, pacer_data_results, k):
        logger.debug("Parsing docket_table entries")
        docket_table_list = []
        docket_table_entries = []
        for t in docket_table_data:
            docket_table_list.append(str(t).strip())
        while("" in docket_table_list) :
            docket_table_list.remove("")

        docket_table_list.pop(0)
        for d in docket_table_list:
            date,link,page,act,docs,attachs = None,None,None,None,None,None
            x = re.findall("<td.*?>(.+?)<\/td>", d)
            try:
                date = x.pop(0)
            except:
                pass

            y = re.findall("\(.+;\s([0-9]{1,3}).+docs\)", d)
            try:
                docs = y[0]
            except:
                pass

            entry = " ".join(x)
            if len(x) > 2:
                act = x.pop()
            else:
                act = entry

            act_strp = self.strip_hyper_links(act)
            data,attaches = self.extract_docket_table_data(entry)
            act = act_strp

            try:
                link = data[0][0]
            except:
                pass
            try:
                page = data[0][1]
            except:
                pass

            docket_details = f"{date}:bkwsplit:{link}:bkwsplit:{page}:bkwsplit:{docs}:bkwsplit:{act}:bkwsplit:{attaches}"
            logger.debug(docket_details)
            docket_table_entries.append(docket_details)
        pacer_data_results[k]['docket_table'] = docket_table_entries

    def extract_docket_table_data(self, entry):        
        l = None
        attachments_var = None
        atts_search_list = []
        l = re.findall("this\.href=\"(.+?)\".*\(([0-9]{1,3})", entry)
        # We need to parse the attachments from the activity feed
        # Could potentially contain Unsecured Creditors as well as files for purchase
        find_loc = entry.find('Attachments')
        # If find(word) found we get all attachments, could be multiple in a single entry
        if find_loc != -1:
            attachments = re.findall("\(Attachments:(.+)", entry)
            # split and append foo to associate attachments with docket entry
            for a in attachments:
                atts_search_list = []
                atts_list = a.split('#') # our delimiter
                for t in atts_list:# get the hyper links
                    atts_search_list.append(re.findall("<a href=\"(.+?)\".+<\/a> (.+)", t.replace('(', '')))
                attachments_var = atts_search_list
        return(l, attachments_var)

    def strip_hyper_links(self, html):
            find_act = None
            scriptOpen, scriptClose = makeHTMLTags("script")
            scriptBody = scriptOpen + scriptOpen.tag_body + scriptClose
            commonHTMLEntity.setParseAction(replaceHTMLEntity)

            # first pass, strip out tags and translate entities
            firstPass = (
                (htmlComment | scriptBody | commonHTMLEntity | anyOpenTag | anyCloseTag)
                .suppress()
                .transformString(str(html))
            )

            # first pass leaves many blank lines, collapse these down
            repeatedNewlines = LineEnd() * (2,)
            repeatedNewlines.setParseAction(replaceWith("\n\n"))
            secondPass = repeatedNewlines.transformString(firstPass)

            # remove strange characters if found
            find_act = re.findall("\\u00a0.+?\) (.+)", secondPass)
            if len(find_act) == 0:
                rdata = secondPass
            else:
                rdata = find_act[0]
            return(rdata)


    def parse_html_table(self,html):
        # create a regular expression to parse the HTML table
        regex = r'<table>(.*?)</table>'
        
        # find all matches of the regular expression
        matches = re.findall(regex, html, flags=re.DOTALL)
        
        # create a list to store the parsed data
        parsed_table_data = []
        
        # loop through each table
        for table in matches:
            # create a list of rows
            rows = re.findall(r'<tr>(.*?)</tr>', table, flags=re.DOTALL)
            
            # create a list to store the parsed data for each row
            parsed_row_data = []
            
            # loop through each row
            for row in rows:
                # create a list of columns
                columns = re.findall(r'<td>(.*?)</td>', row, flags=re.DOTALL)
                
                # add the parsed data from each column to the row list
                parsed_row_data.append(columns)

def main():
    r1 = ResultsParserSvc('sesh')
    #r1.address_parser('Indigo Manor Holdings 3989 Chain Bridge Rd Ste 2 Fairfax, VA 22030 ')
    html = """
    <html><head><link rel="shortcut icon"  href="/favicon.ico"/><title>LIVE database</title>
<SCRIPT LANGUAGE="JavaScript">
							document.cookie="PacerSession=3KDemvtKHhTgJl8D7UdSA6AIdXGSjjMwobFCVcP0JQBEI83biRw2SwLOfU0SLFRgzUSsKhmDCQRDfOPPU43OiyhGLazVZrVdG4UiFrDFatY4N5wvB9J44BhNE2BQcfAi; path=/; domain=.uscourts.gov; secure;"
							</SCRIPT><script type="text/javascript">document.cookie = "PRTYPE=web; path=/;"</script> <script>var default_base_path = "/"; </script> <link rel="stylesheet" type="text/css" href="/css/default.css"><script type="text/javascript" src="/lib/core.js"></script><script type="text/javascript" src="/lib/autocomplete.js"></script><script type="text/javascript" src="/lib/DisableAJTALinks.js"></script><script type="text/javascript">if (top!=self) {top.location.replace(location.href);}</script><script>var default_base_path = "/"; </script></head><body  onLoad='SetFocus()'>
				<div class="noprint">
				<div id="topmenu" class="yuimenubar"><div class="bd">
				<img id="cmecfLogo" class="cmecfLogo" src="/graphics/logo-cmecf-sm.png" alt="CM/ECF" title=""  />
				<ul class="first-of-type">
			
<li class="yuimenubaritem"><a class="yuimenubaritemlabel" href='/cgi-bin/iquery.pl'>Q</u>uery</a></li>
<li class="yuimenubaritem"><a class="yuimenubaritemlabel" href='/cgi-bin/DisplayMenu.pl?Reports&id=-1'>R</u>eports <div class='spritedownarrow'></div></a></li>
<li class="yuimenubaritem"><a class="yuimenubaritemlabel" href='/cgi-bin/DisplayMenu.pl?Utilities&id=-1'>U</u>tilities <div class='spritedownarrow'></div></a></li>
<li class="yuimenubaritem"><a class="yuimenubaritemlabel" onClick="CMECF.MainMenu.showHelpPage(''); return false">Help</a></li>
<li class="yuimenubaritem"><a class="yuimenubaritemlabel" href='/cgi-bin/login.pl?logout'>Log Out</a></li><li class='yuimenubaritem' id='placeholderForAlertsIcon'></li>
				</ul></div>
				<hr class="hrmenuseparator"></div></div>
				
			<script type="text/javascript">
callCreateMenu=function(){
				var fn = "CMECF.MainMenu.renderSimpleMenu";
				if(typeof CMECF.MainMenu.renderSimpleMenu == 'function') {
					CMECF.MainMenu.renderSimpleMenu();
				}
                        }
if (navigator.appVersion.indexOf("MSIE")==-1){window.setTimeout( function(){ callCreateMenu(); }, 1);}else{CMECF.util.Event.addListener(window, "load",  callCreateMenu());}</script> <div id="cmecfMainContent"><input type="hidden" id="cmecfMainContentScroll" value="0"><SCRIPT LANGUAGE="JavaScript">
		var IsForm = false;
		var FirstField;
		function SetFocus() {
			if(IsForm) {
				if(FirstField) {
					var ind = FirstField.indexOf('document.',0);
					if(ind == 0)
					{
						eval(FirstField);
					}
					else
					{
						var Code = "document.forms[0]."+FirstField+".focus();";
						eval(Code);
					}
				} else {
					var Cnt = 0;
					while(document.forms[0].elements[Cnt] != null) {
						try {
							if(document.forms[0].elements[Cnt].type != "hidden" &&
									!document.forms[0].elements[Cnt].disabled &&
									!document.forms[0].elements[Cnt].readOnly) {
								document.forms[0].elements[Cnt].focus();
								break;
							}
						}
						catch(e) {}
						Cnt += 1;
					}
				}
			}
			return(true);
		}
		</SCRIPT>
<CENTER>
<B><FONT SIZE=+1>23-10262</FONT></B>
<B></B>Lexagene Holdings Inc.
<BR>
<B>Case type:</B> bk
<B>Chapter:</B> 7
<B>Asset:</B> Yes
<B>Vol: </B> v
<b>Judge:</b> Christopher J. Panos 
<BR>
<B>Date filed:</B> 02/24/2023
<B>Date of last filing:</B> 02/27/2023
<BR>
</CENTER><BR>
<h2 align=center>Creditors</h2><br><center><TABLE BORDER=0 CELLSPACING=10>
	<TD ALIGN=left><FONT SIZE="+0"><B>British Columbia Securities Commission</B>
<BR>701 West Georgia Street
<BR>P.O. Box 10142, Pacific Centre
<BR>Vancouver, BC V7Y 1L2</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751903)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Commonwealth of Massachusetts</B>
<BR>Department of Unemployment Assistance
<BR>Legal Dept. 1st Fl, Attn.Chief Counsel
<BR>19 Staniford Street
<BR>Boston, MA 02114</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751904)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Computershare</B>
<BR>510 Burrard Street, 3rd Floor
<BR>Vancouver, BC V6C 389</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751905)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Dr. Jane Sykes</B>
<BR>500 Cummings Center, Suite 4550
<BR>Beverly, MA 01915</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751906)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Internal Revenue Service</B>
<BR>P.O. Box 7346
<BR>Philadelphia, PA 19101</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751907)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Joseph Caruso</B>
<BR>500 Cummings Center, Suite 4550
<BR>Beverly, MA 01915</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751908)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Lexagene, Inc</B></FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751909)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Massachusetts Department of Revenue</B>
<BR>Bankruptcy Unit
<BR>P.O. Box 9564
<BR>Boston, MA 02114</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751910)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>McMillan LLP</B>
<BR>Brookfield Place
<BR>181 Bay Street, Suite 4400
<BR>Toronto, ON  M5J 2T3</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751911)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Meridian LGH Holdings 2, LLC</B>
<BR>3811 Turtle Creek Boulevard
<BR>Suite 875
<BR>Dallas, TX 75219</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751912)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Office of the Attorney General</B>
<BR>Fair Labor Division
<BR>Commonwealth of Massachusetts
<BR>One Ashburton Place, 18th Floor
<BR>Boston, MA 02108</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751913)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>RSM Canada LLP</B>
<BR>P.O. Box 4090 STN A
<BR>Lockbox 918960
<BR>Toronto, ON M5W 0E9</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751914)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Securities and Exchange Commission</B>
<BR>Boston Regional Office
<BR>33 Arch Street, 24th Floor
<BR>Boston, MA 02110</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751915)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Securities and Exchange Commission</B>
<BR>100 F Street, NE
<BR>Washington, DC 20549</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751916)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Stephan Mastrocola</B>
<BR>500 Cummings Center, Suite 4550
<BR>Beverly, MA 01915</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751917)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Thomas Slezak</B>
<BR>500 Cummings Center, Suite 4550
<BR>Beverly, MA 01915</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751918)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>Toppan Merrill Corporation</B>
<BR>1 Adelaide Street East
<BR>Suite 3000, P.O. Box 204
<BR>Toronto, ON  M5C 2T3</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751919)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>TSX Venture Exchange</B>
<BR>650 West Georgia Street
<BR>Suite 2700
<BR>Vancouver, BC V6B 4N9</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751920)<br>(cr)</FONT></TD></TR>	<TD ALIGN=left><FONT SIZE="+0"><B>W. Phillip Whitcomb, Esq.</B>
<BR>Munsch Hardt Kopf & Harr, P.C.
<BR>500 N. Akard Street, Suite 3800
<BR>Dallas, TX 75201</FONT></TD>	<TD ALIGN=left><FONT SIZE="+0">(20751921)<br>(cr)</FONT></TD></TR></TABLE></CENTER><HR><CENTER><TABLE BORDER=1 BGCOLOR=white width="400"><TR><TH COLSPAN=4><FONT SIZE=+1 COLOR=DARKRED>PACER Service Center </FONT></TH></TR><TR><TH COLSPAN=4><FONT COLOR=DARKBLUE>Transaction Receipt </FONT></TH></TR><TR></TR><TR></TR><TR><TD COLSPAN=4 ALIGN=CENTER><FONT SIZE=-1 COLOR=DARKBLUE>02/27/2023 10:23:31</FONT></TD></TR><TR><TH ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> PACER Login: </FONT></TH><TD ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> Chrisb7712 </FONT></TH></TD><TH ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> Client Code: </FONT></TH><TD ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> 6430212 </FONT></TD></TR><TR><TH ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> Description: </FONT></TH><TD ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> Creditor List </FONT></TD><TH ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> Search Criteria: </FONT></TH><TD ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> 23-10262 Creditor Type: cr </FONT></TD></TR><TR><TH ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> Billable Pages: </FONT></TH><TD ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> 1 </FONT></TD><TH ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> Cost: </FONT></TH><TD ALIGN=LEFT><FONT SIZE=-1 COLOR=DARKBLUE> 0.10 </FONT></TD></TR><TR></TR><TR></TR></TABLE></CENTER></HR><BR></BR></div></body></html>
    """
    my_data_set = r1.parse_html_data(html)
    print(my_data_set)


# MAIN
if __name__ == '__main__':
    main()


"""
NEW FLOW
- Parse Docket Entries for Petition
    - Ensure this is "non-individual"
    - Check for Sub. V declaration
    - Ensure the pdf does not already exist in S3
    - Download the petition and Save if not, else DL from S3 archive
- Parse Associated Case endpoints
    - Attach associated cases to Main case
- Parse Docket Entries for Unsecured wording
    - Ensure this is NOT a CHILD case(we only parse losses from Parent cases)
    - Ensure this pdf does not already exist in S3
    - Download the unsecured creditors and Save if not, else DL from S3 archive
- Parse Creditors endpoint
    - Download the creditors and save
"""