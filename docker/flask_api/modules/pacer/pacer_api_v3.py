#!/usr/bin/python
# -*- coding: latin-1 -*-

import re
import os, sys
import json
import time
import pprint
import glob
import datetime
import requests, pickle
from os import path
import logging.config
from logtail import LogtailHandler
import lxml.html as lh
from lxml import etree
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
### MODULE SETUP ###
sys.path.insert(0, '/app')
from modules.pacer import config
#from modules.aws.bkw_aws_functions import BkAwsFunctions

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
class PacerApiSvc:
    def __init__(self):
        # init req session
        self.pacer_login_session = requests.Session()
        # AWS configuration
        self.s3bucket_batch_reports = config.s3_bkw_pacer_batch_reports
        self.case_data_full_path = config.case_data_full_path
        # File info
        self.case_data_filename = config.case_data_filename
        self.case_data_full_path = config.case_data_full_path
        # Selenium Setup
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Remote(command_executor=config.chrome_hub, options=options)
        # Setup secrets from ENV VARS
        self.pacer_username = os.environ['PACER_USERNAME']
        self.pacer_password = os.environ['PACER_PASSWORD']
        self.pacer_clientcode = os.environ['PACER_CLIENTCODE']
        self.pacer_cso_login_url = os.environ['PACER_CSO_LOGIN_URL']
        self.pacer_api_url = os.environ['PACER_API_URL']
        # Setup timestamps and cookie name/paths
        self.time_now = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        self.date_now_no_time = datetime.datetime.now().strftime('%Y-%m-%d')
        self.abs_cookie_path = path.dirname(path.abspath(__file__))
        self.pacer_cookie_wildcard = path.join(self.abs_cookie_path, 'cookie_file_*')
        self.pacer_cookie_file = path.join(self.abs_cookie_path, 'cookie_file_') + str(self.time_now)

    def pacer_check_cookie(self):
        """PACER Cookie Check(PCL) - Check if we have cookie on file, if so, check validity
        if the cookie is within 8hrs we'll load and use else need to create a new one

        :set: we set cookie for auth or return expired if not valid
        """
        logger.info('Checking cookies')
        cookie_existing_file = None
        # use glob to search for file wildcard
        glob_search_file = self.pacer_cookie_wildcard
        cookie_existing_file = glob.glob(glob_search_file)

        if cookie_existing_file:
            # split timestamp so we can compare to timedelta
            crap1,crap2,cfdate,cfh,cfm,cfs = cookie_existing_file[0].split('_')
            strpt_setup = cfdate + ' ' + cfh+':'+cfm+':'+cfs
            # set file timestamp and delta for 1hrs
            last_updated =  datetime.datetime.strptime(strpt_setup, '%Y-%m-%d %H:%M:%S')
            time_expired = (last_updated + timedelta(hours=1))
            # check if we passed expiration delta
            if datetime.datetime.now() > time_expired:
                # clean up expired cookie file
                logger.debug('cookies expired')
                os.remove(path.join(self.abs_cookie_path, cookie_existing_file[0]))
                os.remove(path.join(self.abs_cookie_path, 'session_cookies'))
                return('expired')
            else:
                logger.debug('readin cookies')
                # readin valid cookie payload and set as cso token
                f = open(path.join(self.abs_cookie_path, cookie_existing_file[0]))
                self.pacer_login_cso_token = f.read()

                with open(path.join(self.abs_cookie_path, 'session_cookies'), 'rb') as f:
                    self.pacer_login_session.cookies.update(pickle.load(f))
                return(self.pacer_login_session)
        else:
            logger.debug('cookies do not exist')
            return('expired')

    def pacer_session_login(self):
        # PACER LOGIN
        """PACER Login(PCL) - We must pass credentials to login service and store
        credential token for additional API requests

        :return: True if login successful, else False
        """
        logger.debug(f"pacer_session_login triggered")
        login_url = config.pacer_login_url
        try:
            self.driver.get(login_url)
            # find username/email field and send the username itself to the input field
            self.driver.find_element_by_name("loginForm:loginName").send_keys(self.pacer_username)
            time.sleep(5)
            # find password input field and insert password as well
            self.driver.find_element_by_name("loginForm:password").send_keys(self.pacer_password)
            time.sleep(5)
            self.driver.find_element_by_name("loginForm:clientCode").send_keys('6430212')
            time.sleep(5)
            # click login button'
            self.driver.find_element_by_name("loginForm:fbtnLogin").click()
            time.sleep(5)
            self.driver.get(config.pacer_welcome_url)

        except Exception as exception_msg:
            logger.error(f"PACER Login Failed: {exception_msg}")
            self.driver.close()
            exit(1)

        return(self.get_cookies())

    def get_cookies(self):
        logger.debug(f"get_cookies triggered")
        cookies = {}
        selenium_cookies = self.driver.get_cookies()
        for cookie in selenium_cookies:
            cookies[cookie['name']] = cookie['value']
        self.cookies = cookies
        
        logger.info('Pacer Session login successful!')
        with open(path.join(self.abs_cookie_path, 'session_cookies'), 'wb') as f:
            pickle.dump(cookies, f)
        f.close()

        with open(path.join(self.abs_cookie_path, 'session_cookies'), 'rb') as f:
            self.pacer_login_session.cookies.update(pickle.load(f))
        f.close()

        return(self.pacer_login_session)

    def pacer_cso_login(self):
        """PACER Login(PCL) - We must pass credentials to login service and store
        credential token for additional API requests

        :return: True if login successful, else False
        """
        logger.debug(f"pacer_cso_login triggered")
        def_function_name = 'pacer_login'
        # Build requests call paramters, headers and login_url
        login_url = self.pacer_cso_login_url + '/services/cso-auth'
        login_headers = {'content-type': 'application/json', 'accept': 'application/json'}
        login_params = {'loginId': self.pacer_username , 'password': self.pacer_password, 'clientCode': self.pacer_clientcode, 'redactFlag': '1'} #need to remove secret

        try: # attempt PACER login and valid loginResult as 200 does not equate to succesful login
            response = requests.post(url=login_url, headers=login_headers, json=login_params)
            if response.json()['loginResult'] == '0':
                logger.info('Pacer login successful!')
                self.pacer_login_cso_token = response.json()['nextGenCSO']
                # Save session for later use as cookie file
                f = open(self.pacer_cookie_file, "w")
                f.write(self.pacer_login_cso_token)
                f.close()
            else:
                logger.error(f"Pacer LOGIN Failed!: {response.json()}")
                exit(1)
        except Exception as e:
            logger.error(f"PACER CSO Login Failed")
            exit(1)

## DEPRCATED CALL ##
#    def pacer_case_search(self, dfs, dfe):
#        """Pacer Case Search(PCL) - Used to pull JSON data of all filed bankruptcies
#        for Chapter 7/11 - daily. Results can be saved to XML file for $cheaper$
#        testing, avoiding PACER fees ( See comments below )
#
#        :return: True if login successful, else False
#        """
#        search_req = None
#        def_function_name = 'pacer_case_search'
#        # Search PCL
#        search_url = self.pacer_api_url + '/pcl-public-api/rest/cases/find'
#        header_params = {'content-type': 'application/json', 'accept': 'application/json', 'X-NEXT-GEN-CSO': self.pacer_login_cso_token}
#        #search_data = {'dateFiledFrom': dfs,'dateFiledTo': dfe, 'federalBankruptcyChapter': ['7','11']}
#        search_data = {'dateFiledFrom': dfs,'dateFiledTo': dfe, 'federalBankruptcyChapter': ['11']}
#
#
#        logger.info('Running PACER search for 24HR case data')
#        try:
#            search_req = requests.post(search_url, headers=header_params, json=search_data, allow_redirects=True)
#        except Exception as e:
#            logger.error(e, extra={"function_name":def_function_name})
#            exit(1)
#
#        if search_req != None:
#            logger.info('Writing pacer search results to file')
#            try:
#                # Directly from dictionary
#                with open('json_case_data.json', 'w') as outfile:
#                    json.dump(search_req.json(), outfile)
#            except Exception as e:
#                logger.warning(e)
#        else:
#            logger.error('search req was None')
#            exit(1)
#        self.pcl_search_data_json = search_req.json()
#        return(self.pcl_search_data_json)

    def pacer_case_search_batch(self, dfs, dfe):
        """Pacer Case Search(PCL) - Used to pull JSON data of all filed bankruptcies
        for Chapter 7/11 - daily. Results can be saved to JSON file for $cheaper$
        testing, avoiding PACER fees ( See comments below )

        :return: JSON data search success, else False
        """
        #search_req = None
        ## Search PCL
        search_url = self.pacer_api_url + '/pcl-public-api/rest/cases/download'
        header_params = {'content-type': 'application/json', 'accept': 'application/json', 'X-NEXT-GEN-CSO': self.pacer_login_cso_token}
        search_data = {'dateFiledFrom': dfs,'dateFiledTo': dfe, 'federalBankruptcyChapter': ['7','11']}

        logger.info('Running PACER batch search for 24HR case data')
        # Init case batch search
        try:
            search_req = requests.post(search_url, headers=header_params, json=search_data, allow_redirects=True)  # get batch job ID
            if search_req.status_code == 200:
                logger.debug('Pacer batch queue successful')
                data = search_req.json()
                return data
            else:
                logger.error('Report Search Failed, probably an issue with PACER')
                logger.debug(search_req.text)
                exit(1)
        except Exception as e:
            logger.error(e)
            exit(1)

    def batch_report_status(self):
        """Pacer Case Search(PCL) - Batch search report status
        We wait for a report that is ready to download or fail and exit

        :return: JSON data search success, else exit(1)
        """        
        search_url = self.pacer_api_url + '/pcl-public-api/rest/cases/reports'
        header_params = {'content-type': 'application/json', 'accept': 'application/json', 'X-NEXT-GEN-CSO': self.pacer_login_cso_token}
        logger.info('checking report status')
        try:
            search_req = requests.get(search_url, headers=header_params, allow_redirects=True) #check status of batch - Completed = ready for download
            if search_req.status_code == 200:
                logger.debug('Pacer batch status successful')
                data = search_req.json()
                return data
            else:
                logger.error('Report Status Failed, probably an issue with PACER')
                logger.debug(search_req.text)
                exit(1)
        except Exception as e:
            logger.error(e)
            exit(1)

    def batch_report_download(self, report_id):
        """Pacer Case Search(PCL) - Batch report download and save to JSON file
        
        DELETE the batch report after succesful download

        :return: Write JSON to file, else exit(1)
        """                
        # if status is completed - download reportid recorded from above
        #BAWSF = BkAwsFunctions()
        search_url = self.pacer_api_url + '/pcl-public-api/rest/cases/download/' + str(report_id)
        header_params = {'content-type': 'application/json', 'accept': 'application/json', 'X-NEXT-GEN-CSO': self.pacer_login_cso_token}
        object_name_w_timestamp = f"{self.case_data_filename}_{str(self.date_now_no_time)}"
        try:
            search_req = requests.get(search_url, headers=header_params, allow_redirects=True)
            if search_req.status_code == 200:
                logger.debug('Pacer batch download successful')
                logger.info('Writing pacer search results to file')
                try:
                    # Directly from dictionary
                    with open(self.case_data_full_path, 'w') as outfile:
                        json.dump(search_req.json(), outfile)                   
                    #BAWSF.upload_file(file_name=self.case_data_full_path, bucket=self.s3bucket_batch_reports, object_name=object_name_w_timestamp)
                except Exception as e:
                    logger.warning(e)

                self.pcl_search_data_json = search_req.json()
                self.batch_report_delete(report_id)
            else:
                logger.error('Batch Report Download Failed')
                logger.debug(search_req.text)
                exit(1)
        except Exception as e:
            logger.error(e)
            exit(1)

    def batch_report_delete(self, report_id):
        # clean up batch report
        search_url = self.pacer_api_url + '/pcl-public-api/rest/cases/reports/' + str(report_id)
        header_params = {'content-type': 'application/json', 'accept': 'application/json', 'X-NEXT-GEN-CSO': self.pacer_login_cso_token}
        try:
            search_req = requests.delete(search_url, headers=header_params, allow_redirects=True)
            if search_req.status_code == 200:
                logger.debug('Batch Report Delete Succesful')
            else:
                logger.debug('Batch Report Delete Failed')
                pass
        except Exception as e:
            logger.debug('Batch Report Delete Failed')
            logger.error(e)
            pass
        return True

    def pacer_data_from_file(self, file_name=config.case_data_full_path, bucket=config.s3_bkw_pacer_batch_reports):
        """PACER data from file - This allows us to parse saved pacer data in turn
        saving on PACER fees, as they are charged on each search for every result returned

        :param file_name: The local file name of XML data from PACER
        :return: True if login successful, else False
        """
        logger.info('Getting PACER data from File: ' + str(file_name))
        object_name_w_timestamp = f"{self.case_data_filename}_{str(self.date_now_no_time)}"

        #BAWF = BkAwsFunctions()
        #BAWF.download_file(file_name=file_name, bucket=bucket, object_name=object_name_w_timestamp)
        try:
            with open(file_name) as json_file:
                data = json.load(json_file)
        except Exception as e:
                logger.error('pacer data from file failed: ',e)
                exit(1)

        try:
            logger.debug(data['receipt'])
        except Exception as e:
            logger.warning('Receipt info not available')

        self.pcl_search_data_json = data
        return(self.pcl_search_data_json)

    def pcl_parse_json(self):
        """JSON Parser for JSON data returned from PACER API
        Allows for data extraction from XML data sets from PACER for CL use

        Ensures ONLY companies are in the list of PDFs to pull/parse by regex below

        :param xml_data: XML data set returned from API
        :return: True if login successful, else False
        """
        logger.info('Parse JSON data returned from PACER case search')

        # We only care about Chapter 7/11/ business bankruptcies - build regex for match
        ## THIS ISN'T THE BEST IDEA BUT ONLY THING VIABLE CURRENTLY WITH PACER LIMITATIONS
        #TODO: These need to move to Database - easy access/growing company word bank
        regex_list = []
        reg_find_list_end = config.reg_find_list_end
        reg_find_list_end_no_space = config.reg_find_list_end
        reg_find_list_any = config.reg_find_list_any
        for l in reg_find_list_end:
            regex_list.append(rf".+?[\w\,] {l}?$""")

        for l in reg_find_list_any:
            regex_list.append(rf".*{l}.*""")

        count = 0
        business_bk_dict = {}
        regex_matches_list = []

        total_bk_count = len(self.pcl_search_data_json['content'])
        while (count < len(self.pcl_search_data_json['content'])):
            case_title = (self.pcl_search_data_json['content'][count]['caseTitle'])
            bk_chapter = (self.pcl_search_data_json['content'][count]['bankruptcyChapter'])
            count += 1

            if bk_chapter == '11':
                regex_matches_list.append(case_title)
            else:
                for regex in regex_list:
                    s = re.search(regex, str(case_title), re.IGNORECASE)
                    if s:
                        regex_matches_list.append(s[0])
                        
        total_bk_bus_count = len(regex_matches_list)
        logger.info('Total BKs: ' + str(total_bk_count) + ' Total Business BKs: ' + str(total_bk_bus_count))
        self.reg_match_list = regex_matches_list
        logger.info(self.reg_match_list)

    def build_pacer_case_search_data_results(self):
        logger.info('Building pacer case search results')

        count = 0
        pacer_case_search_results = {}
        try:
            while (count < len(self.pcl_search_data_json['content'])):
                case_title = (self.pcl_search_data_json['content'][count]['caseTitle'])
                if case_title in self.reg_match_list:
                    pacer_case_search_results[case_title] = {}
                    pacer_case_search_results[case_title]['court_id'] = self.pcl_search_data_json['content'][count]['courtId'][:-1] #strip pacer 'K'
                    pacer_case_search_results[case_title]['date_filed'] = self.pcl_search_data_json['content'][count]['dateFiled']
                    pacer_case_search_results[case_title]['cs_year'] = self.pcl_search_data_json['content'][count]['caseYear']
                    pacer_case_search_results[case_title]['cs_number'] = self.pcl_search_data_json['content'][count]['caseNumber']
                    pacer_case_search_results[case_title]['case_number'] = self.pcl_search_data_json['content'][count]['caseNumberFull']
                    pacer_case_search_results[case_title]['cs_office'] = self.pcl_search_data_json['content'][count]['caseOffice']
                    pacer_case_search_results[case_title]['cs_chapter'] = self.pcl_search_data_json['content'][count]['bankruptcyChapter']
                    pacer_case_search_results[case_title]['case_link'] = self.pcl_search_data_json['content'][count]['caseLink']
                    pacer_case_search_results[case_title]['pdf_dl_status'] = 'incomplete'
                count += 1
        except Exception  as e:
            logger.error(e)
            exit(1)

        self.pcsd_results = pacer_case_search_results
        return(self.pcsd_results)

    def pacer_dkt_rpt(self, case_link):
        """Pacer Case Search(PCL) - This function calls Docket Report endpoint
        and parses DOCKET REPORT html for POST link that we'll use later to execute

        :case_link: Case Link for Bankruptcy - used in GET call below
        :user_session: This is our PACER auth/cookies and allows API Calls to services
        :return: User Session and Docket Report Number found in parsing
        """
        logger.info('Running PacerDocketReport and parsing HTML response')

        # Search PCL
        dkt_rpt_num = False
        # TODO: add endpoint configs and hit each one (associated/case-summary/creditors)
        # next each config will need to be parsed accordingly
        pacer_docket_report_link = case_link.replace('iqquerymenu.pl','DktRpt.pl')
        logger.debug(pacer_docket_report_link)
        try:
            search_req = self.pacer_login_session.get(pacer_docket_report_link, timeout=10, allow_redirects=True)
        except Exception as e:
            logger.error("Failed to connect to court: " + pacer_docket_report_link)
            logger.debug(pacer_docket_report_link)
            logger.error(e)
            return False

        try:
            get_dkt_rpt_number = r"<FORM ENCTYPE=\'multipart\/form-data\' method=POST action=\"\.\.\/cgi-bin\/DktRpt\.pl\?(.+?)\""
            get_dkt_rpt_number_nodot = r"<FORM ENCTYPE=\'multipart\/form-data\' method=POST action=\"\/cgi-bin\/DktRpt\.pl\?(.+?)\""
            s = re.search(get_dkt_rpt_number, str(search_req.text))
            sr = re.search(get_dkt_rpt_number_nodot, str(search_req.text))
            if s:
                group_match = s.group(0)
                crap, dkt_rpt_num = group_match.split('?')
                dkt_rpt_num = dkt_rpt_num.strip('"')
            elif sr:
                group_match = sr.group(0)
                crap, dkt_rpt_num = group_match.split('?')
                dkt_rpt_num = dkt_rpt_num.strip('"')
            else:
                logger.warning('No Form number found!')
                logger.debug(search_req.text)
        except Exception as e:
            logger.debug("Getting Docket Report Number FAILED")
            logger.debug(pacer_docket_report_link)
            logger.error(e)

        logger.debug('Docket Report Number: ' + str(dkt_rpt_num))
        self.docker_report_number = dkt_rpt_num
        return(dkt_rpt_num)

    def pacer_post_for_html(self, case_link, case_num, date_filed):
        """Pacer Case Search(PCL) - Used to pull XML data of all filed bankruptcies
        for Chapter 7/11/15 - daily. Results can be saved to XML file for $cheaper$
        testing, avoiding PACER fees ( See comments below )

        :return: True if login successful, else False
        """

        split_case_link = case_link.split('?')
        search_url = split_case_link[0].replace('iqquerymenu.pl','DktRpt.pl?') + str(self.docker_report_number)

        header_params = {'content-type': 'application/x-www-form-urlencoded'}
        search_data = {'all_case_ids': split_case_link[1], 'case_num': case_num,
        'date_type': 'filed', 'date_from': '', 'date_to': '', 'documents_numbered_from_':'',
        'documents_numbered_to_':'', 'terminated_parties': 'on', 'include_pdf_headers': 'on',
        'page_count': 'on', 'output_format': 'html', 'sort1':'oldest date first'}

        logger.info('Getting Docket Report HTML Table')
        try:
            response = self.pacer_login_session.post(search_url, headers=header_params, data=search_data, allow_redirects=True)
        except Exception as e:
            logger.warning(e)
            pass

        if response != None and response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            #logger.debug(soup)
            logger.debug("soup successful")
        else:
            logger.error('API GET FAILED')
            logger.debug('status_code: ' + str(response.status_code))
            logger.debug('status_reason: ' + response.reason)

        self.pacer_post_html_soup = soup
        return(soup, self.pacer_login_session)
        #logger.debug(search_req.text)
        #return(search_req.text)

    def get_html_file_links(self, pacer_link):
        """Pacer Case Search(PCL) - Used to run get requests against PACER
        returning the HTML output as result

        :return: HTML results, if success, else None
        """
        pacer_files = []
        files_returned = []
        response = None
        header_params = {'content-type': 'text/html'}

        logger.info('Getting HTML file links')
        print(pacer_link)
        try:
            response = self.pacer_login_session.get(pacer_link, headers=header_params, allow_redirects=True)
        except Exception as e:
            logger.warning(e)
            pass

        if response != None and response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            #logger.debug(soup)
            logger.debug("soup successful")
        else:
            logger.error(f'API GET FAILED: {response}')
            return '500'

        if re.search('value=\"View Document\"', str(soup)):
            logger.debug(f"Single File found: {pacer_link}")
            files_returned.append({'filename': 'Main Document', 'link': pacer_link})
        else:
            logger.debug(f"Multi File[s] found: {pacer_link}")
            tables = soup.find_all('table')
            pacer_files = re.findall('this\.href=\"(.+?)\".*<\/td><td><\/td><td>(.+?)<\/td>', str(tables))
            for p in pacer_files:
                fn = p[1].strip()
                link = p[0]
                files_returned.append({'filename': fn, 'link': link})
                
        return(files_returned)

    def post_file_links(self, file_link):
        response = None
        logger.info(f'Downloading file: {file_link}')
        header_params = {'content-type': 'application/x-www-form-urlencoded', 'referer': file_link}
        search_data = {'got_receipt': '1', 'pdf_header': 1}

        logger.info(f'Downloading PACER file: {file_link}')
        try:
            response = self.pacer_login_session.post(file_link, headers=header_params, data=search_data, allow_redirects=True)
        except Exception as e:
            logger.warning(e)
            pass

        if response != None and response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            #logger.debug(soup)
            logger.debug("soup successful")
            return(soup)
        else:
            logger.error('API GET FAILED')
            logger.debug('status_code: ' + str(response.status_code))
            logger.debug('status_reason: ' + response.reason)
            return '500'

def main():
    # PACER API SERVICE
    p1 = PacerApiSvc()
    pacer_login_session = None
    cookie_check = p1.pacer_check_cookie()
    if cookie_check == 'expired':
        pacer_login_session = p1.pacer_session_login()
        p1.pacer_cso_login()
    else:
        logger.debug('cookies still valid')
        pacer_login_session = cookie_check

    if pacer_login_session == None:
        logger.error(f"PACER login session failed: {pacer_login_session}")
        exit(1)
    #print(p1.get_html_file_links('https://ecf.nysb.uscourts.gov/doc1/126022476616')) #https://ecf.nysb.uscourts.gov/doc1/126022476523
    #print(p1.get_html_file_links('https://ecf.nysb.uscourts.gov/doc1/126022476523'))
    #p1.post_file_links('https://ecf.nysb.uscourts.gov/doc1/126022476523')
    #p1.runit()
    #p1.pacer_case_search('2022-02-24', '2022-02-25')
    #p1.pacer_data_from_file()
    #p1.pcl_parse_json()
    #p1.build_pacer_case_search_data_results()
    #print(p1.pacer_case_search_batch('''{"reportId":200001858,"status":"RUNNING","startTime":null,"endTime":null,"recordCount":null,"unbilledPageCount":null,"downloadFee":null,"pages":null,"sort":{"orders":[]},"searchType":"COURT_CASE","criteria":{"searchType":"COURT_CASE","courtId":[],"requestType":"Batch","requestSource":"API","caseType":[],"dateFiledFrom":"2022-03-25","dateFiledTo":"2022-03-25","federalBankruptcyChapter":["7","11"],"natureOfSuit":[]}}'''))
    #data = (p1.pacer_case_search_batch('2022-02-25', '2022-02-25'))
    #data = {}
    #data['reportId'] = 1805
    #r_status = p1.batch_report_status()
    #print(r_status)
    #count = 0
    #while (len(r_status['content']) > count):
        #print(r_status['content'][count]['reportId'], r_status['content'][count]['status'])
        #if r_status['content'][count]['reportId'] == data['reportId'] and r_status['content'][count]['status'] == 'COMPLETED':
            #p1.batch_report_download(data['reportId'])
        #elif r_status['content'][count]['reportId'] == data['reportId'] and r_status['content'][count]['status'] == 'RUNNING':
            #time.sleep(15)
            #r_status = p1.batch_report_status(data['reportId'])
            #if r_status['content'][count]['reportId'] == data['reportId'] and r_status['content'][count]['status'] == 'COMPLETED':
                #p1.batch_report_download(data['reportId'])
            #else:
                #logger.error('Still running')
                #logger.debug(r_status)
                #exit(1)
        #elif r_status['content'][count]['reportId'] == data['reportId'] and r_status['content'][count]['status'] == 'FAILED':
            #exit(1)
        #else:
            #pass
        #count += 1
    #p1.batch_report_delete(300002378)
#1806
#1807
#1808
#1809
#200001854
#200001855
#200001856
#200001857
#200001858

#100002405 COMPLETED
# COMPLETED
# COMPLETED
# COMPLETED
# COMPLETED

#'''{"receipt":null,"pageInfo":{"number":0,"size":54,"totalPages":1,"totalElements":6,"numberOfElements":6,"first":true,"last":true},"content":[{"reportId":100002393,"status":"COMPLETED","startTime":"2022-03-25T10:03:00.000-0500","endTime":"2022-03-25T10:03:01.000-0500","recordCount":2002,"unbilledPageCount":0,"downloadFee":0.0,"pages":38,"criteria":{"searchType":"COURT_CASE","courtId":[],"requestType":"Batch","requestSource":"API","caseType":[],"dateFiledFrom":"2022-03-23","dateFiledTo":"2022-03-25","federalBankruptcyChapter":["7","11"],"natureOfSuit":[]},"sort":{"orders":[]}},{"reportId":100002394,"status":"COMPLETED","startTime":"2022-03-25T10:03:26.000-0500","endTime":"2022-03-25T10:03:27.000-0500","recordCount":2002,"unbilledPageCount":38,"downloadFee":3.8000000000000003,"pages":38,"criteria":{"searchType":"COURT_CASE","courtId":[],"requestType":"Batch","requestSource":"API","caseType":[],"dateFiledFrom":"2022-03-23","dateFiledTo":"2022-03-25","federalBankruptcyChapter":["7","11"],"natureOfSuit":[]},"sort":{"orders":[]}},{"reportId":100002395,"status":"COMPLETED","startTime":"2022-03-25T10:03:59.000-0500","endTime":"2022-03-25T10:04:00.000-0500","recordCount":2002,"unbilledPageCount":38,"downloadFee":3.8000000000000003,"pages":38,"criteria":{"searchType":"COURT_CASE","courtId":[],"requestType":"Batch","requestSource":"API","caseType":[],"dateFiledFrom":"2022-03-23","dateFiledTo":"2022-03-25","federalBankruptcyChapter":["7","11"],"natureOfSuit":[]},"sort":{"orders":[]}},{"reportId":100002396,"status":"COMPLETED","startTime":"2022-03-25T10:05:01.000-0500","endTime":"2022-03-25T10:05:01.000-0500","recordCount":2002,"unbilledPageCount":38,"downloadFee":3.8000000000000003,"pages":38,"criteria":{"searchType":"COURT_CASE","courtId":[],"requestType":"Batch","requestSource":"API","caseType":[],"dateFiledFrom":"2022-03-23","dateFiledTo":"2022-03-25","federalBankruptcyChapter":["7","11"],"natureOfSuit":[]},"sort":{"orders":[]}},{"reportId":300002356,"status":"FAILED","startTime":"2022-03-25T09:55:01.000-0500","endTime":"2022-03-25T09:55:01.000-0500","recordCount":0,"unbilledPageCount":null,"downloadFee":null,"pages":0,"criteria":{"searchType":"COURT_CASE","courtId":[],"requestType":"Batch","requestSource":"API","caseType":[],"dateFiledFrom":"2022-03-24","dateFiledTo":"2022-03-25","federalBankruptcyChapter":["7","11"],"natureOfSuit":[]},"sort":{"orders":[]}}]}'''

# MAIN
if __name__ == '__main__':
    main()


"""
=========================
PACER MODULE USE AND FLOW
=========================

Pacer login and Cookie Storage
Download batch case data
Create data object of all Business cases found(using regex/word bank)
Loop through that data object, scraping data from PACER on each case
Data Obejcts to be pulled:
    Case Name (from Batch Results)
    Case Number (from Batch Results)
    Associated Cases (qryAscCases.pl) - linked using case numbers/names
    Creditors (CreditorQry.pl)
    Unsecured Creditors (Parse PDF)
    Represented by
    Trustee
"""