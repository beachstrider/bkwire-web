#!/usr/bin/python
# -*- coding: latin-1 -*-

import re
import pprint
import usaddress
from os import path
import urllib.request
import logging.config
import lxml.html as lh
import pandas as pd
from lxml import etree
import xml.etree.ElementTree as ET
from time import strptime
from bs4 import BeautifulSoup
from datetime import date, timedelta
from modules.aws.check_s3_objects import check_against_s3_objects, download_pdf_from_s3_archive

### MODULE SETUP ###


## Set up logging
log_file_path = path.join(path.dirname(path.abspath(__file__)), '/app/logging/logging.ini')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)
logger_list = ['boto', 'boto3', 'chardet', 'urllib3', 'botocore', 's3transfer', 'PIL']
for i in logger_list:
    logging.getLogger(i).setLevel(logging.CRITICAL) #sets all #logging sources to crit level


# Setup globals
xmlDict = {}
pdf_dl_pages = []
html_table_dic = {}
pp = pprint.PrettyPrinter(indent=4)
today = date.today().strftime('%m/%d/%Y')
class ResultsParserSvc:
    def __init__(self, pls):
        logging.info('Init results parser')
        self.pacer_login_session = pls

    def address_parser(self, addy):
        logging.debug('Address to parse: ' + addy)
        company_name = None
        company_city = None
        company_state = None
        company_zip = None

        try:
            adr = usaddress.tag(addy)
        except Exception as e:
            logging.warning(f"unable to successfully parse addy: {e}")

        try:
            company_name = adr[0]['BuildingName']
        except:
            pass
        try:
            company_name = adr[0]['Recipient']
        except:
            pass
        try:
            company_city = adr[0]['PlaceName']
        except:
            pass
        try:
            company_state = adr[0]['StateName']
        except:
            pass
        try:
            company_zip = adr[0]['ZipCode']
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
        # TODO: See if the pandas parsing fixes our nested link issues and builds into our case/refresh and DL of documents
        logging.info('Parsing HTML table to Dictionary')

        a_href_link = {}
        html_table_dic[k] = {}
        tax_id_ein = None
        html_table_dic[k]['tax_id_ein'] = None
        html_table_dic[k]['debtor_name'] = None
        html_table_dic[k]['debtor_address'] = None
        html_table_dic[k]['docket_table'] = None

        html_table_list = []
        my_dke_to_append = []
        docket_table_list = []
        my_test_list_results = []

        #Regex for TAXID
        regex_tax_id  = r"Tax ID \/ EIN: (\d+-\d+)"
        #Regex for Debtor Information
        #regex_debtor_info = r"Debtor\d?\d?(?s)(.*)Tax ID"
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
                logging.debug('debtor_addy: ' + debtor_address)
                # Increment table count
                table_count += 1
            # remove last random string
            if len(docket_table_list) > 0:
                docket_table_list.pop()
            else:
                logging.debug("docket_table_list=0")
        except Exception as e:
            logging.info('Parsing HTML tables to Dict FAILED')
            logging.debug(tables)
            logging.error(e)

        try:
            # get href link for entries
            tags = soup.find_all('a')
            for t in tags:
                if t.text.isdigit():
                    if re.search(r"^/doc1/", t.attrs['href']):
                        a_href_link[t.text] = t.attrs['href']
        except Exception as e:
            logging.info('Parsing HREF for links FAILED')
            logging.debug(tags)
            logging.error(e)

        try:
            # Parse HTML table with docket entries for entries to Download
            for l in docket_table_list:
                logging.debug(l)
                split_list = l.split()
                if split_list[0].isdigit():
                        my_test_list_results.append(l)
        except Exception as e:
            logging.info('Parse HTML entries for DL FAILED')
            logging.error(e)

        if len(my_test_list_results) > 0:
            try:
                # Sort our list to ensure we always download entry 1 (petition for filing)
                my_test_list_results.sort()
                # Now search for any other filings that include 'Unsecure Creditors'
                for m in my_test_list_results[1:]:
                    if re.search(r"Unsecured", m):
                        logging.debug(f"Found separate creditors filing")
                        my_dke_to_append.append(m.lstrip())
                my_dke_to_append.append(my_test_list_results[0].lstrip())

                # Combine a_href link to docket entries we want to DL
                for l in my_dke_to_append:
                    html_table_dic[k][l] = {}
                    if l[0] in a_href_link:
                        html_table_dic[k][l] = a_href_link[l[0]]
                    else:
                        pass
            except Exception as e:
                logging.info('Sort/Parse HTML results FAILED!')
                logging.error(e)
        else:
            logging.info('Docket Entries list was empty and FAILED')
            logging.debug(docket_table_list)

        try: # Lets build a data object with all our things
            html_table_dic[k]['tax_id_ein'] = tax_id_ein
            html_table_dic[k]['debtor_name'] = html_table_list[0]
            html_table_dic[k]['debtor_address'] = debtor_address
            html_table_dic[k]['docket_table'] = docket_table
        except Exception as e:
            logging.info('Debtor additional info was NULL')
            logging.debug(k)
            logging.error(e)

        # clear tables for next case in loop
        a_href_link = {}
        docket_table_list = []

        logging.debug(html_table_dic)
        self.soup_to_html_dic = html_table_dic
        return(html_table_dic)

    def parse_html_tables(self, html_tables_results, pacer_data_results, pacer_pdf_results):
        html_table_key_list = ['tax_id_ein', 'debtor_name', 'debtor_address', 'docket_table']
        for key,val in html_tables_results.items():
            pdf_doc_url = []
            pacer_pdf_results[key] = {}
            pacer_data_results[key]['pdf_dl_skip'] = False
            modified_case_number = pacer_data_results[key]['case_number'].split(':')
            modified_case_link   = pacer_data_results[key]['case_link'].split('/cgi-bin')
            referer_url          = pacer_data_results[key]['case_link'].replace('iqquerymenu.pl','DktRpt.pl')
            pdf_file_name        = pacer_data_results[key]['court_id'] +'.'+ modified_case_number[1]

            pdf_doc_count = 0
            if type(val) is dict:
                for k in val:
                    if k in html_table_key_list:
                        pass
                    elif isinstance(html_tables_results[key][k], dict):
                        for hk in html_tables_results[key][k]:
                            pdf_doc_url.append(modified_case_link[0] + hk)
                    else:
                        pdf_doc_url.append(modified_case_link[0] + html_tables_results[key][k])

            if html_tables_results[key]['debtor_address']:
                logging.debug('HTML_TABLE_RESULTS(debtor_address): ' + str(html_tables_results[key]['debtor_address']))
                try:
                    #TODO: this need to move to IAP module
                    adr = usaddress.tag(html_tables_results[key]['debtor_address'])
                except Exception as e:
                    pacer_data_results[key]['company_address'] = None
                    pacer_data_results[key]['company_city'] = None
                    pacer_data_results[key]['company_state'] = None
                    pacer_data_results[key]['company_zip'] = None
                    pacer_data_results[key]['company_industry'] = None
                    logging.error(e)
                try:
                    pacer_data_results[key]['company_city'] = adr[0]['PlaceName']
                except:
                    pacer_data_results[key]['company_city'] = None
                try:
                    pacer_data_results[key]['company_state'] = adr[0]['StateName']
                except:
                    pacer_data_results[key]['company_state'] = None
                try:
                    pacer_data_results[key]['company_zip'] = adr[0]['ZipCode']
                except:
                    pacer_data_results[key]['company_zip'] = None
                try:
                    pacer_data_results[key]['company_industry'] = 'Unknown'
                except:
                    pacer_data_results[key]['company_industry'] = None
                try:
                    pacer_data_results[key]['company_address'] = adr[0]['AddressNumber'] + ' ' + adr[0]['StreetName'] + ' ' + adr[0]['StreetNamePostType']
                except:
                    pacer_data_results[key]['company_address'] = html_tables_results[key]['debtor_address']
            else:
                pacer_data_results[key]['company_address'] = None
                pacer_data_results[key]['company_city'] = None
                pacer_data_results[key]['company_state'] = None
                pacer_data_results[key]['company_zip'] = None
                pacer_data_results[key]['company_industry'] = None

            while pdf_doc_count < len(pdf_doc_url):
                split_case_link = pacer_data_results[key]['case_link'].split('?')
                pdf_file_name_full_wpage = pdf_file_name +'.'+ split_case_link[1] +'-'+ str(pdf_doc_count) + '.pdf'
                pacer_pdf_results[key][pdf_file_name_full_wpage] = False
                ##############################################################
                #TODO:                                                      #
                #CHECK IF PDF EXISTS IN S3 bucket VS. re-downloading in PACER#
                check_s3_exists = check_against_s3_objects(pdf_file_name_full_wpage, referer_url)
                if check_s3_exists == False:
                    if pdf_doc_url != None:
                        logging.info('NO S3 object exists in archive')
                        #this goes back to import, trigger download and perform logic below for results
                        self.download_pdf_href(pdf_doc_url[pdf_doc_count], referer_url, pdf_file_name_full_wpage, pacer_data_results, key, pacer_pdf_results)
                    else:
                        pass
                else:
                    logging.info('S3 exists in archive')
                    results = download_pdf_from_s3_archive(pdf_file_name_full_wpage, referer_url)
                    if results != False:
                        pacer_data_results[key]['pdf_dl_status'] = 'complete'
                        pacer_data_results[key]['pdf_filename'] = pdf_file_name_full_wpage
                        pacer_pdf_results[key][pdf_file_name_full_wpage] = True
                        logging.info('Download from S3 archive SUCCESS')
                    else:
                        pacer_data_results[key]['pdf_dl_status'] = 'incomplete'
                        pacer_data_results[key]['pdf_filename'] = None
                        logging.info('Download from S3 archive FAILED')
                        logging.error(results)

                pdf_doc_count += 1
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
        logging.info('Running POST: ' + href_link + ' caseID: ' + split_case_link[1])

        try: #Using all our parsing to this point - attempt to Download PDF
            response = self.pacer_login_session.post(href_link, headers=header_params, data=dl_pdf_data, timeout=20, allow_redirects=True)
            logging.debug('response: ' + str(response))
        except Exception as e:
            logging.info('PDF POST Request FAILED! ' + href_link)
            logging.error(e)
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
                logging.info('FAILED: Response is None or Unknown type' + str(href_link))
        else:
            logging.info('Request response was False')
            pass

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
        pacer_data_results[key]['pdf_filename'] = None
        split_case_link_slash = case_link.split('/')
        logging.info('Running POST(download) from temp_url: ' + split_case_link_slash[2])

        soup = BeautifulSoup(r.content, 'lxml')
        tags = soup.find_all('a')
        for t in tags:
            try:
                s = re.search(r"(.+show_temp.+)", str(t.attrs['href']))
                v = re.search(r"doc1", str(t.attrs['href']))
                if s:
                    pdf_temp_url = 'https://' + split_case_link_slash[2] + s.group(0)
                    try:
                        urllib.request.urlretrieve(pdf_temp_url, pdf_full_path_wname)
                        pacer_data_results[key]['pdf_dl_status'] = 'complete'
                        pacer_data_results[key]['pdf_filename'] = pdf_fn
                        #pacer_data_results[key]['pdf_dl_pages'] = pdf_dl_pages.append(pdf_full_path_wname)
                    except Exception as e:
                        logging.info('FAILED: Unable to download PDF: ' + pdf_temp_url)
                        logging.error(e)
                elif v:
                    if t.text == '1':
                        pdf_nested_href = 'https://' + split_case_link_slash[2] + t.attrs['href']
                        self.download_pdf_href(pdf_nested_href, case_link, pdf_fn, pacer_data_results, key, pacer_pdf_results)
                else:
                    pass
            except Exception as e:
                logging.info('temp_url download failed, trying something else..')
                logging.error(e)
                pass


    def pdf_from_content(self, r, path_file_name, pacer_data_results, key, pacer_pdf_results, file_name):
        logging.info('Downloading PDF from content response')
        pacer_data_results[key]['pdf_filename'] = None
        #logging.info(r.text)
        try:
            with open(path_file_name, 'wb') as f:
                f.write(r)
            f.close()
            pacer_data_results[key]['pdf_dl_status'] = 'complete'
            pacer_data_results[key]['pdf_filename'] = file_name
        except Exception as e:
            logging.info('Downloading PDF from content FAILED')
            logging.error(e)


    def docket_table_parse(self, docket_table_data):
        docket_table_list = []
        docket_table_entries = []
        for t in docket_table_data:
            docket_table_list.append(str(t).strip())
        while("" in docket_table_list) :
            docket_table_list.remove("")

        docket_table_list.pop(0)
        for d in docket_table_list:
            date,link,page,act,docs = None,None,None,None,None
            x = re.findall("<td.*?>(.+?)<\/td>", d)
            try:
                date = x[0]
            except Exception as e:
                pass
            y = re.findall("\(.+;\s([0-9]{1,3}).+docs\)", d)
            try:
                docs = y[0]
            except Exception as e:
                pass
            if len(x) <= 2:
                l = re.findall("this\.href=\"(.+?)\".*\(([0-9]{1,3})", x[1])
            else:
                l = re.findall("this\.href=\"(.+?)\".*\(([0-9]{1,3})", x[2])
            try:
                link = l[0][0]
            except Exception as e:
                pass
            try:
                page = l[0][1]
            except Exception as e:
                pass
            try:
                act = x[3]
            except Exception as e:
                pass
            docket_details = f"{date}:bkwsplit:{link}:bkwsplit:{page}:bkwsplit:{docs}:bkwsplit:{act}"
            logging.debug(docket_details)
            docket_table_entries.append(docket_details)
        return(docket_table_entries)


def main():
    r1 = ResultsParserSvc('sesh')
    r1.address_parser('Indigo Manor Holdings 3989 Chain Bridge Rd Ste 2 Fairfax, VA 22030 ')


# MAIN
if __name__ == '__main__':
    main()
