#!/usr/bin/python

import re
import sys
import boto3
import datetime
import shortuuid
import logging.config
from re import match
from os import listdir, path
from os.path import isfile, join
from trp import Document
from botocore.exceptions import ClientError
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
## IMPORT CUSTOM MODULES ##
sys.path.insert(0, '/app')
from modules.parsers.parse_results_download_pdf import ResultsParserSvc
from modules.address.international_parser import IntAddyParse
from modules.aws import textrac_v3_config
## Set up logging
log_file_path = path.join(path.dirname(path.abspath(__file__)), '/app/logging/logging.ini')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)
logger_list = ['boto', 'boto3', 'chardet', 'urllib3', 'botocore', 's3transfer', 'PIL']
for i in logger_list:
    logging.getLogger(i).setLevel(logging.CRITICAL) #sets all #logging sources to crit level

# GET Datetime NOW
now  = datetime.datetime.now()
config_create_date = now.strftime('%Y%d%m%H%M%S')

# Amazon S3 client
s3_client = boto3.client('s3')

# Amazon Textract client
textract = boto3.client('textract')

s3_resource = boto3.resource('s3')

# globals
count = 0
official_form = []
my_data_object = {}
unsecured_creditor_information = {}
estimated_creditors_list = {'1': '49', '50': '99', '100': '199', \
'200': '999', '1,000': '5,000', '5001': '10,000', '10,001': '25,000',\
'25,001': '50,000', '100,002': '100,002', None: None}
#'More than 100,000'
estimated_assets_liabilities = {'0': '50,000', '50,001': '100,000', \
'100,001': '500,000', '500,001': '1,000,000', '1,000,001': '10,000,000', \
'10,000,001': '50,000,000', '50,000,001': '100,000,000', \
'100,000,001': '500,000,000', '500,000,001': '1,000,000,000',
'1,000,000,001': '10,000,000,000', '10,000,000,001': '50,000,000,000',\
'50,000,000,001': '50,000,000,001', None: None}
#'More than 50 billion'

def parse_204(s3_bucket_name, doc_name):
    """Parse 'Official Form 204' for tabled data sets;
    Unsecured creditor information should be parsed here

    :param s3_bucket_name: Bucket used to house S3 objects
    :param doc_name: S3 object name. Pull this object down to parse
    :return: True if file was uploaded, else False
    """
    #TODO: Parse company names first before address if name follows similar convention:
    #{Address to parse:  375 e 154th street llc 5014 16th avenue brooklyn, ny 11204"}
    list_204_data = []
    regex_matches_list = []
    rps = ResultsParserSvc(None)
    iap = IntAddyParse()
    # Parse PDF Table data via PNG
    logging.info("Parsing 204 info: " + doc_name)

    try:
        # Call Amazon Textract
        response = textract.analyze_document(
            Document={
                'S3Object': {
                    'Bucket': s3_bucket_name,
                    'Name': doc_name
                }
            },
            FeatureTypes=["TABLES"])

        doc = Document(response)

        count = 0
        warning = ""
        for page in doc.pages:
            for table in page.tables:
                for r, row in enumerate(table.rows):
                    count += 1
                    index_list = []
                    list_204_data = []
                    phone_list = None
                    email_list = None
                    full_address = None
                    full_address_pobox = None
                    unsecured_claim_value = None
                    itemName  = ""
                    for c, cell in enumerate(row.cells):
                        test_string_digit = str(cell.text).strip()
                        if r >= 2 and test_string_digit.isdigit() == False:
                            if cell.text is None:
                                pass
                            else:
                                list_204_data.append(cell.text)
                        if(c == 0):
                            itemName = cell.text
                        elif(c == 4 and isFloat(cell.text)):
                            value = float(cell.text)
                            if(value > 1000):
                                warning += "{} is greater than $1000.".format(itemName)
                    if len(list_204_data) == 7:
                        #needed to ensure uniqueness
                        try:
                            phone_list,email_list = get_email_phone(list_204_data[1])
                        except:
                            pass
                        address_object = iap.parse_address(list_204_data[0])
                        suuid = shortuuid.uuid()
                        print(phone_list)
                        print(email_list)
                        print(f"comp: {address_object[0]}")
                        comp_name_no_numb = re.search(r'^[0-9]{1,2} (.+?)$', str(address_object[0]))
                        if comp_name_no_numb is None:
                            comp_name = address_object[0]
                        else:
                            comp_name = comp_name_no_numb.group(1)
                        print(comp_name)
                        print(address_object[2])
                        print(address_object[3])
                        print(list_204_data[2])
                        print(list_204_data[6].replace("$","").replace(",",""))
                        #ncode_results = check_industry_word_bank(address_object[0])
                        #if ncode_results != None:
                        #    ncode = ncode_results
                        logging.debug(list_204_data)
                    elif len(list_204_data) == 8:
                        #needed to ensure uniqueness
                        try:
                            phone_list,email_list = get_email_phone(list_204_data[2])
                        except:
                            pass
                        address_object = iap.parse_address(list_204_data[1])
                        creditor_with_count = list_204_data[1] + '__' + str(count) + '__'
                        print(phone_list)
                        print(email_list)
                        comp_name_no_numb = re.search(r'^[0-9]{1,2} (.+?)$', str(address_object[0]))
                        if comp_name_no_numb is None:
                            comp_name = address_object[0]
                        else:
                            comp_name = comp_name_no_numb.group(1)
                        print(comp_name)
                        print(address_object[2])
                        print(address_object[3])
                        print(list_204_data[3])
                        print(list_204_data[7].replace("$","").replace(",",""))                        
                        logging.debug(list_204_data)
                    else:
                        logging.debug('No Data found within 204: ' + str(len(list_204_data)))
                        logging.debug('PNG='+str(doc_name))
                        logging.debug(str(list_204_data))
        if(warning):
            print("\nReview needed:\n====================\n" + warning)

    except Exception as e:
        logging.error(f"{doc_name}: {e}")

def isFloat(input):
    """Helper Function for Table Parsing

    :param input: Input from 204 Table processing
    :return: True if PDF was converted, else False
    """
    try:
      float(input)
    except ValueError:
      return False
    return True

def parse_206(data_set):
    """Parse 'Official Form 206' for tabled data sets;
    Unsecured creditor information should be parsed here

    :param data_set: Raw data in a list for parsing
    :return: True if file was uploaded, else False
    """
    rps = ResultsParserSvc(None)
    iap = IntAddyParse()
    #TODO: Parse company names first before address if name follows similar convention:
    #{Address to parse:  375 e 154th street llc 5014 16th avenue brooklyn, ny 11204"}

    # Parse PDF KEY/VALUE Pairs via PNG
    listToStr = []
    index_data_set_list = []
    stopwords = textrac_v3_config.rem_word
    #print(stopwords)
    for word in list(data_set):  # iterating on a copy since removing will mess things up
        if word in stopwords:
            #print(word)
            data_set.remove(word)

    for d in data_set: # Remove conflicting PDF pages before parsing
        s = re.search('list others to be notified about unsecured claims', str(d))
        if not s is None:
            index_of_data_set = data_set.index(s.group(0))
            for x in range(index_of_data_set,len(data_set)):
                del data_set[index_of_data_set]

    for d in data_set:
        s = re.search('^[1-3]\.[0-9]{1,3}', str(d))
        if not s is None:
            #print(s.group(0), data_set.index(s.group(0)))
            try:
                index_of_data_set = data_set.index(s.group(0))
                index_data_set_list.append(index_of_data_set)
            except Exception as e:
                logging.warning(data_set)

    for d in data_set:
        s = re.search('^[1-3]\.[0-9]{1,3}', str(d))
        if not s is None:
            total_index_set_size = len(data_set)
            if len(index_data_set_list) > 1:
                data_set_list = []
                range_start = index_data_set_list.pop(0)
                range_end = index_data_set_list[0]
                for x in range(range_start,range_end):
                    data_set_list.append(data_set[x])
                listToStr.append(' '.join([str(elem) for elem in data_set_list]))
            elif len(index_data_set_list) == 1:
                data_set_list = []
                range_start = index_data_set_list.pop(0)
                range_end = total_index_set_size
                for x in range(range_start,range_end):
                    data_set_list.append(data_set[x])
                listToStr.append(' '.join([str(elem) for elem in data_set_list]))
    
    count = 0
    regex_dict = textrac_v3_config.regex_206_dict
    for l in listToStr:
        print(l)#
        nature_claim=creditor_info=partial_claim=indicate_claim=deduction_value=creditor_industry=unsecured_claim_value=creditor_contact_info='na'
        for g in regex_dict:
            re_results = re.search(g['value'], str(l))
            if not re_results is None:
                if g['key'] == 'rs_pob':
                    try:
                        print(f'found w rs_rob')
                        creditor_info = re_results.group(3) +' '+ re_results.group(4) +' '+ re_results.group(5)
                        unsecured_claim_value = re_results.group(2)
                        nature_claim = re_results.group(6)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_pob Matched but failed to add objects')
                        logging.debug(l)
                elif g['key'] == 'rs_w_claim':
                    try:
                        print(f'found w claim')                        
                        creditor_info = re_results.group(3) +' '+ re_results.group(4)
                        unsecured_claim_value = re_results.group(2)
                        nature_claim = re_results.group(5)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_w_claim Matched but failed to add objects')
                        logging.debug(l)
                elif g['key'] == 'rs_n2_claim':
                    try:
                        print(f'found rs_n_claim') #rs_n2_claim
                        creditor_info = re_results.group(3) +' '+ re_results.group(4)
                        unsecured_claim_value = re_results.group(2)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_n_claim Matched but failed to add objects')
                        logging.debug(l)
                elif g['key'] == 'rs_n_claim':
                    try:
                        print(f'found rs_n_claim')
                        creditor_info = re_results.group(3) +' '+ re_results.group(4)
                        unsecured_claim_value = re_results.group(2)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_n_claim Matched but failed to add objects')
                        logging.debug(l)
                elif g['key'] == 'rs_unk':
                    try:
                        print(f'found rs_unk')
                        creditor_info = re_results.group(2) +' '+ re_results.group(3)
                        unsecured_claim_value = re_results.group(1)
                        nature_claim = re_results.group(4)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_unk Matched but failed to add objects')
                        logging.debug(l)
                elif g['key'] == 'rs_rest':
                    try:
                        print(f'found rs_rest')
                        creditor_info = re_results.group(2) +' '+ re_results.group(3)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_rest Matched but failed to add objects')
                        logging.debug(l)
                elif g['key'] == 'rs_rest_unk':
                    try:
                        print(f'found rs_rest_unk')
                        creditor_info = re_results.group(2)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_rest_unk Matched but failed to add objects')
                        logging.debug(l)
                elif g['key'] == 'rs_search_itv1':
                    try:
                        print(f'found rs_search_itv1')
                        creditor_info = re_results.group(2)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_search_it Matched but failed to add objects')
                        logging.debug(l)                        
                elif g['key'] == 'rs_search_itv2':
                    try:
                        print(f'found rs_search_itv2')
                        creditor_info = re_results.group(1)
                        unsecured_claim_value = re_results.group(2)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_search_it Matched but failed to add objects')
                        logging.debug(l)
                elif g['key'] == 'rs_search_it':
                    try:
                        print(f'found rs_search_it')
                        creditor_info = re_results.group(2)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_search_it Matched but failed to add objects')
                        logging.debug(l)
                elif g['key'] == 'rs_search_it_unk':
                    try:
                        print(f'found rs_search_it_unk')
                        creditor_info = re_results.group(2) + re_results.group(3)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logging.warning('206 - rs_search_it_unk Matched but failed to add objects')
                        logging.debug(l)
                else:
                    logging.debug('206 No Regex match: ' + l)
        #needed to ensure uniqueness
        #print(creditor_info)
        address_object = iap.parse_address(creditor_info)
        #print(address_object)
        print(f'Unsecured Claim: {unsecured_claim_value.replace("$","").replace(",","")}')
        if address_object[0] is None:
            comp_name = creditor_info.split()
            comp_name = comp_name[0]
        else:
            comp_name = address_object[0]
        print(f"Comp Name: {comp_name}")
        print(f"Comp State: {address_object[2]}")
        print(f"Comp Zip: {address_object[3]}")

def find_adjacents(val, items):
    i = items.index(val)
    return items[i:i+4]

def rawtext_pdffromimage(documentName, s3BucketName):
    """Parse PNG files for raw text in order to correctly identify fields

    :param s3_bucket_name: Bucket used to house S3 objects
    :param doc_name: S3 object name. Pull this object down to parse
    :return: True if file was uploaded, else False
    """
    my_list = []
    # Call Amazon Textract
    try:
        response = textract.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': s3BucketName,
                    'Name': documentName
                }
            })

        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                my_list.append(str(item["Text"]).lower())
    except Exception as e:
        logging.warning(f'Detect Document Text Failed {documentName}: {e}')
        pass

    return my_list

def main():
    #raw_results = rawtext_pdffromimage('439302ed-cf5d-4751-be86-a66ea37c4ea6-1.png','bpwa.parse-png')
    #print(raw_results)
#    parse_206(raw_results)
#    raw_results = rawtext_pdffromimage('4ee5b60b-fe6a-4ab1-9039-74a5bef0db41-1.png','bpwa.parse-png')
#    #print(raw_results)
#    parse_206(raw_results)
#    raw_results = rawtext_pdffromimage('4ee5b60b-fe6a-4ab1-9039-74a5bef0db41-2.png','bpwa.parse-png')
#    #print(raw_results)
#    parse_206(raw_results)
#    raw_results = rawtext_pdffromimage('4ee5b60b-fe6a-4ab1-9039-74a5bef0db41-3.png','bpwa.parse-png')
#    #print(raw_results)
#    parse_206(raw_results)
#    raw_results = rawtext_pdffromimage('4ee5b60b-fe6a-4ab1-9039-74a5bef0db41-4.png','bpwa.parse-png')
#    #print(raw_results)
#    parse_206(raw_results)            
    #raw_results = rawtext_pdffromimage('ac867dfc-f67e-4085-9211-68c28559c104-3.png','bpwa.parse-png')
    #print(raw_results)
    #parse_206(raw_results)
    #raw_results = rawtext_pdffromimage('ac867dfc-f67e-4085-9211-68c28559c104-4.png','bpwa.parse-png')
    #print(raw_results)
    #parse_206(raw_results)            
#    raw_results = rawtext_pdffromimage('2848f2cd-8007-410b-8720-cdd4780f5207-2.png','bpwa.parse-png')
#    #print(raw_results)
#    parse_206(raw_results)        
#    raw_results = rawtext_pdffromimage('2848f2cd-8007-410b-8720-cdd4780f5207-3.png','bpwa.parse-png')
#    #print(raw_results)
#    parse_206(raw_results)
    parse_204('bpwa.parse-png', '3b69d1b5-485a-44b6-a078-bd5742e788c9-1.png')
    
# MAIN
if __name__ == '__main__':
    main()