#!/usr/bin/python

import re
import os
import sys
import boto3
import datetime
import logging.config
from logtail import LogtailHandler
from re import match
import shortuuid
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
from modules.database.db_connec_v2 import lookup_naics_prefixes
from modules.database.db_select import dbSelectItems
from modules.industry.industry_scraper import WebScrape
from modules.address.international_parser import IntAddyParse
from modules.aws import textrac_v3_config

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

def convert_pdf2png(file, s3BucketName, skip):
    """Convert PDF pages to PNG files for processing;
    Upload PNG files to create an S3 object for parsing

    :param file: PDF File to convert to PNG
    :return: True if PDF was converted, else False
    """
    pdf_path_w_file = 'results/' + file
    #pdf_path_w_file = file
    split_file = pdf_path_w_file.split('/')
    file = split_file[1]
    if skip == False:
        logger.info("S3 PDF Upload in progress")
        upload_file(pdf_path_w_file, 'bpwa.pdf-storage', file)
    else:
        logger.info("SKIPPING: S3 PDF Upload - Already Exists")
        pass

    png_path = 'results/pdf2png/'

    try:
        images_from_path = convert_from_path(pdf_path_w_file, output_folder=png_path, fmt='png')
    except Exception as e:
        logger.info('PDF to PNG conversion FAILED')
        logger.debug(pdf_path_w_file)
        logger.error(e)

    logger.info("S3 PNG Upload in progress")
    png_files = [f for f in listdir(png_path) if isfile(join(png_path, f))]
    for f in png_files:
        abs_path_w_file = png_path + f
        upload_file(abs_path_w_file, s3BucketName, f)

    return(png_files)

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name
    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except Exception as e:
        logger.info('S3 Upload Failed!')
        logger.error(e)
        pass
    return True

def copy_object(bucket, key_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # Upload the file
    logger.info(f"Running S3 copy job: {key_name}")

    try:
        #response = s3_resource.Object(bucket, key_name).put(Body=str(object))
        # Copy object A as object B
        new_obejct = key_name.replace("creditors", "misc")
        s3_resource.Object(bucket, new_obejct).copy_from(
        CopySource=f"{bucket}/{key_name}")
    except Exception as e:
        logger.info('S3 COPY Failed!')
        logger.error(e)
        pass
    return True

def delete_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name
    # Upload the file
    try:
        response = s3_client.delete_object(Key=file_name, Bucket=bucket)
    except Exception as e:
        logger.info('S3 Delete Failed!')
        logger.error(e)
        pass
    return True

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

def parse_201(s3_bucket_name, doc_name, data_object_results, key, **kwargs):
    """Parse 'Official Form 201' for KEY/Value pairs for Estimated Info

    :param s3_bucket_name: Bucket used to house S3 objects
    :param doc_name: S3 object name. Pull this object down to parse
    :return: True if file was uploaded, else False
    """
    # Parse PDF KEY/VALUE Pairs via PNG
    logger.info("Parsing 201 info: " + doc_name)
    # Call Amazon Textract
    my_selected_fields = []
    response = textract.analyze_document(
        Document={
            'S3Object': {
                'Bucket': s3_bucket_name,
                'Name': doc_name
            }
        },
        FeatureTypes=["FORMS"])

    doc = Document(response)
    regex_matches_list = []
    regex_number_values = r"^([0-9]{1,3}.+)"
    regex_more_than_val = r"^(More than.+)"
    regex_dollar_values = r"^(\$[0-9]{1,3}.+)"
    regex_list = [regex_number_values, regex_more_than_val, regex_dollar_values]

    """ LOGIC EQUALS
    If all 3 matches are found:
        check values against list
        next compare assets/liabilities - higher value = EL

    If not all 3 matches are found:
        take into account page numbers
        2 matches page 3 = creditors/assets (check against list)
        1 matches page 3 = creditors
        2 matches page 4 = assets/liabilities (compare - higher value = EL)
        1 matches page 4 = liabilities
    """

    for page in doc.pages:
        for field in page.form.fields:
            if str(field.value) == 'SELECTED' or str(field.value) == 'X' or str(field.value) == 'None':
                my_selected_fields.append(field.key)

    for i in my_selected_fields:
        for regex in regex_list:
            s = re.search(regex, str(i))
            if s:
                regex_matches_list.append(s.group(0))

    logger.debug(regex_matches_list)

    if len(regex_matches_list) == 3:
        return(match_3(regex_matches_list, data_object_results, key))
    elif len(regex_matches_list) == 2:
        return(match_2(regex_matches_list, data_object_results, key, **kwargs))
    elif len(regex_matches_list) == 1:
        return(match_1(regex_matches_list, data_object_results, key, **kwargs))
    else:
        logger.info('Unable to parse 201 data')
        return(data_object_results)


def match_1(rml, data_object_results, key, **kwargs):
    estimated_creditors_min = None
    estimated_creditors_max = None
    estimated_liabilities_min = None
    estimated_liabilities_max = None

    if kwargs.get('pg') == '3':
        logger.debug('match: 1' + 'page: 3')
        for e in rml:
            e = e.replace('$','')
            new_val = e.replace('-',' ')
            init_val = new_val.split()
            init_val[0] = check_key(init_val[0])
            if init_val[0] in estimated_creditors_list.keys():
                logger.debug('Estimated Creditors: ' + init_val[0] + '-' + estimated_creditors_list[init_val[0]])
                estimated_creditors_min = init_val[0].replace(',','')
                estimated_creditors_max = estimated_creditors_list[init_val[0]].replace(',','')
                data_object_results[key]['estimated_creditors_min'] = int(estimated_creditors_min)
                data_object_results[key]['estimated_creditors_max'] = int(estimated_creditors_max)
            elif init_val[0] in estimated_assets_liabilities.keys():
                logger.debug('Estimated Assets: ' + init_val[0] + '-' + estimated_assets_liabilities[init_val[0]])
                estimated_assets_min = init_val[0].replace(',','')
                estimated_assets_max = estimated_assets_liabilities[init_val[0]].replace(',','')
                data_object_results[key]['estimated_assets_min'] = int(estimated_assets_min)
                data_object_results[key]['estimated_assets_max'] = int(estimated_assets_max)

    elif kwargs.get('pg') == '4':
        logger.debug('match: 1' + 'page: 4')
        for e in rml:
            e = e.replace('$','')
            new_val = e.replace('-',' ')
            init_val = new_val.split()
            init_val[0] = check_key(init_val[0])
            if init_val[0] in estimated_assets_liabilities.keys():
                logger.debug('Estimated Liabilities: $' + init_val[0] + '-$' + estimated_assets_liabilities[init_val[0]])
                estimated_liabilities_min = init_val[0].replace(',','')
                estimated_liabilities_max = estimated_assets_liabilities[init_val[0]].replace(',','')
                data_object_results[key]['estimated_liabilities_min'] = int(estimated_liabilities_min)
                data_object_results[key]['estimated_liabilities_max'] = int(estimated_liabilities_max)

    return(data_object_results)

def match_2(rml, data_object_results, key, **kwargs):

    estimated_assets_min = None
    estimated_assets_max = None
    estimated_creditors_min = None
    estimated_creditors_max = None
    estimated_liabilities_min = None
    estimated_liabilities_max = None

    compare_items = []
    if kwargs.get('pg') == '3':
        logger.debug('match: 2' + 'page: 3')
        for e in rml:
            e = e.replace('$','')
            new_val = e.replace('-',' ')
            init_val = new_val.split()
            init_val[0] = check_key(init_val[0])
            if init_val[0] in estimated_creditors_list.keys():
                logger.debug('Estimated Creditors: ' + init_val[0] + '-' + estimated_creditors_list[init_val[0]])
                estimated_creditors_min = init_val[0].replace(',','')
                estimated_creditors_max = estimated_creditors_list[init_val[0]].replace(',','')
                data_object_results[key]['estimated_creditors_min'] = int(estimated_creditors_min)
                data_object_results[key]['estimated_creditors_max'] = int(estimated_creditors_max)

            elif init_val[0] in estimated_assets_liabilities.keys():
                logger.debug('Estimated Assets: ' + init_val[0] + '-' + estimated_assets_liabilities[init_val[0]])
                estimated_assets_min = init_val[0].replace(',','')
                estimated_assets_max = estimated_assets_liabilities[init_val[0]].replace(',','')
                data_object_results[key]['estimated_assets_min'] = int(estimated_assets_min)
                data_object_results[key]['estimated_assets_max'] = int(estimated_assets_max)

    elif kwargs.get('pg') == '4':
        logger.debug('match: 2' + 'page: 4')
        for e in rml:
            e = e.replace('$','')
            new_val = e.replace('-',' ')
            init_val = new_val.split()
            init_val[0] = check_key(init_val[0])
            if init_val[0] in estimated_creditors_list.keys():
                logger.debug('Estimated Creditors: ' + init_val[0] + '-' + estimated_creditors_list[init_val[0]])
                estimated_creditors_min = init_val[0].replace(',','')
                estimated_creditors_max = estimated_creditors_list[init_val[0]].replace(',','')
                data_object_results[key]['estimated_creditors_min'] = int(estimated_creditors_min)
                data_object_results[key]['estimated_creditors_max'] = int(estimated_creditors_max)

            if init_val[0] in estimated_assets_liabilities.keys():
                drop_commas = init_val[0].replace(',','')
                compare_items.append(int(drop_commas))
                # NEED TO SORT LIST AND TAKE THE LIST IN ORDER (1,2,3) PULL K/V PAIR FROM DIC
                compare_items.sort()
                try:
                    ea = place_value(compare_items[0])
                except Exception as e:
                    ea = None
                    logger.warning(compare_items)
                try:
                    el = place_value(compare_items[1])
                except Exception as e:
                    el = None
                    logger.warning(compare_items)
                data_object_results[key]['estimated_assets_min'] = str(ea).replace(',','')
                data_object_results[key]['estimated_assets_max'] = str(estimated_assets_liabilities[ea]).replace(',','')
                data_object_results[key]['estimated_liabilities_min'] = str(el).replace(',','')
                data_object_results[key]['estimated_liabilities_max'] = str(estimated_assets_liabilities[el]).replace(',','')
                logger.debug('Estimated Assets: $' + str(ea) + '-$' + str(estimated_assets_liabilities[ea]))
                logger.debug('Estimated Liabilities: $' + str(el) + '-$' + str(estimated_assets_liabilities[el]))
            else:
                data_object_results[key]['estimated_assets_min'] = estimated_assets_min
                data_object_results[key]['estimated_assets_max'] = estimated_assets_max
                data_object_results[key]['estimated_liabilities_min'] = estimated_liabilities_min
                data_object_results[key]['estimated_liabilities_max'] = estimated_liabilities_max

    return(data_object_results)

def match_3(rml, data_object_results, key):
    logger.debug('match: 3')
    data_object_results[key]['estimated_assets_min'] = None
    data_object_results[key]['estimated_assets_max'] = None
    data_object_results[key]['estimated_creditors_min'] = None
    data_object_results[key]['estimated_creditors_max'] = None
    data_object_results[key]['estimated_liabilities_min'] = None
    data_object_results[key]['estimated_liabilities_max'] = None

    compare_items = []
    for e in rml:
        e = e.replace('$','')
        new_val = e.replace('-',' ')
        init_val = new_val.split()
        init_val[0] = check_key(init_val[0])
        if init_val[0] in estimated_creditors_list.keys():
            logger.debug('Estimated Creditors: ' + init_val[0] + '-' + estimated_creditors_list[init_val[0]])
            estimated_creditors_min = init_val[0].replace(',','')
            estimated_creditors_max = estimated_creditors_list[init_val[0]].replace(',','')
            data_object_results[key]['estimated_creditors_min'] = int(estimated_creditors_min)
            data_object_results[key]['estimated_creditors_max'] = int(estimated_creditors_max)

        if init_val[0] in estimated_assets_liabilities.keys():
            drop_commas = init_val[0].replace(',','')
            compare_items.append(int(drop_commas))
            # NEED TO SORT LIST AND TAKE THE LIST IN ORDER (1,2,3) PULL K/V PAIR FROM DIC
            compare_items.sort()
            try:
                ea = place_value(compare_items[0])
            except Exception as e:
                ea = None
                logger.warning(compare_items)
            try:
                el = place_value(compare_items[1])
            except Exception as e:
                el = None
                logger.warning(compare_items)

            if ea == None:
                data_object_results[key]['estimated_assets_min'] = (ea)
            else:
                data_object_results[key]['estimated_assets_min'] = (ea).replace(',','')

            rem_com_ea = str(estimated_assets_liabilities[ea]).replace(',','')
            data_object_results[key]['estimated_assets_max'] = (rem_com_ea)

            if el == None:
                data_object_results[key]['estimated_liabilities_min'] = (el)
            else:
                data_object_results[key]['estimated_liabilities_min'] = (el).replace(',','')

            rem_com_el = str(estimated_assets_liabilities[el]).replace(',','')
            data_object_results[key]['estimated_liabilities_max'] = (rem_com_el)
            logger.debug('Estimated Assets: $' + str(ea) + '-$' + str(estimated_assets_liabilities[ea]))
            logger.debug('Estimated Liabilities: $' + str(el) + '-$' + str(estimated_assets_liabilities[el]))

    return(data_object_results)

def parse_205(**kwargs):
    data_object_results = kwargs['pacer_data_results']
    logger.info(f"Parsing 205 info")
    for key in kwargs['pacer_data_results']:
        data_object_results[key]['estimated_assets_min'] = -1
        data_object_results[key]['estimated_creditors_min'] = -1
        data_object_results[key]['estimated_liabilities_min'] = -1
        data_object_results[key]['naics_code'] = 511
        data_object_results[key]['involuntary'] = True

    return data_object_results

def place_value(number):
    return ("{:,}".format(number))

def check_key(list_key):
    logger.debug("Checking Key")
    #Transform words into numbers
    new_list_key = list_key
    try:
        more_than_match = re.match("More than+", list_key)
        if more_than_match:
            new_list_key = list_key.replace('More than ', '')
            new_list_key = new_list_key.replace('100,000', '100,002')
            logger.debug("Key Found: More than")
    except:
        pass

    try:
        million = re.match("+million", list_key)
        if million:
            new_list_key = list_key.replace(' million', ',000,000')
            logger.debug("Key Found: million")
    except:
        pass

    try:
        billion = re.match("+billion", list_key)
        if billion:
            new_list_key = list_key.replace(' billion', ',000,000,000')
            logger.debug("Key Found: billion")
    except:
        pass

    logger.debug(new_list_key)
    return new_list_key

def get_email_phone(payload):
    # Create phone regex.
    phoneRegex = re.compile(r'''(
        (\d{3}|\(\d{3}\))? # area code
        (\s|-|\.)? # separator
        (\d{3}) # first 3 digits
        (\s|-|\.) # separator
        (\d{4}) # last 4 digits
        (\s*(ext|x|ext.)\s*(\d{2,5}))? # extension
        )''', re.VERBOSE)

    # Create email regex.
    emailRegex = re.compile(r'''(
        [a-zA-Z0-9._%+-] + #username
        @                   # @symbole
        [a-zA-Z0-9.-] +     # domain
        (\.[a-zA-Z]{2,4})   # dot-something
        )''', re.VERBOSE)

    # Find matches in the clipboard text.
    text = str(payload)
    matches_phone = []
    matches_email = []
    for groups in phoneRegex.findall(text):
        phoneNum = '-'.join([groups[1], groups[3], groups[5]])
        if groups[8] != '':
            phoneNum += ' x' + groups[8]
        matches_phone.append(phoneNum)
    for groups in emailRegex.findall(text):
        matches_email.append(groups[0])

    return(matches_phone, matches_email)

def parse_204(s3_bucket_name, doc_name, data_object_results, key, ncode):
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
    logger.info("Parsing 204 info: " + doc_name)

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
                        #address_object = rps.address_parser(list_204_data[0])
                        address_object = iap.parse_address(list_204_data[0])
                        suuid = shortuuid.uuid()
                        creditor_with_count = list_204_data[0] + '__' + str(suuid) + '__'
                        data_object_results[key][creditor_with_count] = {}
                        data_object_results[key][creditor_with_count]['creditor_phone'] = phone_list
                        data_object_results[key][creditor_with_count]['creditor_email'] = email_list
                        comp_name_no_numb = re.search(r'^[0-9]{1,2} (.+?)$', str(address_object[0]))
                        if comp_name_no_numb is None:
                            comp_name = address_object[0]
                        else:
                            comp_name = comp_name_no_numb.group(1)                        
                        data_object_results[key][creditor_with_count]['creditor_company_name'] = comp_name
                        data_object_results[key][creditor_with_count]['creditor_company_state'] = address_object[2]
                        data_object_results[key][creditor_with_count]['creditor_company_zip'] = address_object[3]
                        data_object_results[key][creditor_with_count]['nature_of_claim'] = list_204_data[2]
                        data_object_results[key][creditor_with_count]['unsecured_claim_value'] = list_204_data[6].replace("$","").replace(",","")
                        #ncode_results = check_industry_word_bank(address_object[0])
                        #if ncode_results != None:
                        #    ncode = ncode_results
                        data_object_results[key][creditor_with_count]['industry'] = ncode
                        logger.debug(list_204_data)
                    elif len(list_204_data) == 8:
                        #needed to ensure uniqueness
                        try:
                            phone_list,email_list = get_email_phone(list_204_data[2])
                        except:
                            pass
                        address_object = iap.parse_address(list_204_data[1])
                        creditor_with_count = list_204_data[1] + '__' + str(count) + '__'
                        data_object_results[key][creditor_with_count] = {}
                        data_object_results[key][creditor_with_count]['creditor_phone'] = phone_list
                        data_object_results[key][creditor_with_count]['creditor_email'] = email_list
                        comp_name_no_numb = re.search(r'^[0-9]{1,2} (.+?)$', str(address_object[0]))
                        if comp_name_no_numb is None:
                            comp_name = address_object[0]
                        else:
                            comp_name = comp_name_no_numb.group(1)                        
                        data_object_results[key][creditor_with_count]['creditor_company_name'] = comp_name
                        data_object_results[key][creditor_with_count]['creditor_company_state'] = address_object[2]
                        data_object_results[key][creditor_with_count]['creditor_company_zip'] = address_object[3]
                        data_object_results[key][creditor_with_count]['nature_of_claim'] = list_204_data[3]
                        data_object_results[key][creditor_with_count]['unsecured_claim_value'] = list_204_data[7].replace("$","").replace(",","")
                        #ncode_results = check_industry_word_bank(address_object[0])
                        #if ncode_results != None:
                        #    ncode = ncode_results
                        data_object_results[key][creditor_with_count]['industry'] = ncode
                        logger.debug(list_204_data)
                    else:
                        logger.debug('No Data found within 204: ' + str(len(list_204_data)))
                        logger.debug('PNG='+str(doc_name))
                        logger.debug(str(list_204_data))
        if(warning):
            print("\nReview needed:\n====================\n" + warning)

    except Exception as e:
        logger.error(f"{doc_name}: {e}")

    return(data_object_results)

def parse_206(data_set, dn, data_object_results, key, ncode=511):
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
    logger.info("Parsing 206 info: " + dn )
 
    listToStr = []
    index_data_set_list = []
    stopwords = textrac_v3_config.rem_word

    for word in list(data_set):  # iterating on a copy since removing will mess things up
        if word in stopwords:
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
            try:
                index_of_data_set = data_set.index(s.group(0))
                index_data_set_list.append(index_of_data_set)
            except Exception as e:
                logger.warning(data_set)

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

    regex_dict = textrac_v3_config.regex_206_dict
    for l in listToStr:
        #print(l)
        nature_claim=creditor_info=partial_claim=indicate_claim=deduction_value=creditor_industry=unsecured_claim_value=creditor_contact_info='na'
        for g in regex_dict:
            re_results = re.search(g['value'], str(l))
            if not re_results is None:
                if g['key'] == 'rs_pob':
                    try:
                        creditor_info = re_results.group(3) +' '+ re_results.group(4) +' '+ re_results.group(5)
                        unsecured_claim_value = re_results.group(2)
                        nature_claim = re_results.group(6)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_pob Matched but failed to add objects')
                        logger.debug(l)
                elif g['key'] == 'rs_w_claim':
                    try:
                        creditor_info = re_results.group(3) +' '+ re_results.group(4)
                        unsecured_claim_value = re_results.group(2)
                        nature_claim = re_results.group(5)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_w_claim Matched but failed to add objects')
                        logger.debug(l)
                elif g['key'] == 'rs_n2_claim':
                    try:
                        creditor_info = re_results.group(3) +' '+ re_results.group(4)
                        unsecured_claim_value = re_results.group(2)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_n_claim Matched but failed to add objects')
                        logger.debug(l)
                elif g['key'] == 'rs_n_claim':
                    try:
                        creditor_info = re_results.group(3) +' '+ re_results.group(4)
                        unsecured_claim_value = re_results.group(2)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_n_claim Matched but failed to add objects')
                        logger.debug(l)
                elif g['key'] == 'rs_unk':
                    try:
                        creditor_info = re_results.group(2) +' '+ re_results.group(3)
                        unsecured_claim_value = re_results.group(1)
                        nature_claim = re_results.group(4)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_unk Matched but failed to add objects')
                        logger.debug(l)
                elif g['key'] == 'rs_rest':
                    try:
                        creditor_info = re_results.group(2) +' '+ re_results.group(3)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_rest Matched but failed to add objects')
                        logger.debug(l)
                elif g['key'] == 'rs_rest_unk':
                    try:
                        creditor_info = re_results.group(2)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_rest_unk Matched but failed to add objects')
                        logger.debug(l)
                elif g['key'] == 'rs_search_itv1':
                    try:
                        creditor_info = re_results.group(2)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_search_it Matched but failed to add objects')
                        logger.debug(l)                        
                elif g['key'] == 'rs_search_itv2':
                    try:
                        creditor_info = re_results.group(1)
                        unsecured_claim_value = re_results.group(2)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_search_it Matched but failed to add objects')
                        logger.debug(l)
                elif g['key'] == 'rs_search_it':
                    try:
                        creditor_info = re_results.group(2)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_search_it Matched but failed to add objects')
                        logger.debug(l)
                elif g['key'] == 'rs_search_it_unk':
                    try:
                        creditor_info = re_results.group(2) + re_results.group(3)
                        unsecured_claim_value = re_results.group(1)
                        break
                    except Exception as e:
                        logger.warning('206 - rs_search_it_unk Matched but failed to add objects')
                        logger.debug(l)
                else:
                    logger.debug('206 No Regex match: ' + l)

        #needed to ensure uniqueness
        address_object = iap.parse_address(creditor_info)
        if address_object[0] is None:
            comp_name = creditor_info.split()
            comp_name = comp_name[0]
        else:
            comp_name = address_object[0]

        #needed to ensure uniqueness
        suuid = shortuuid.uuid()
        creditor_with_count = creditor_info + '__' + str(suuid) + '__'
        data_object_results[key][creditor_with_count] = {}

        data_object_results[key][creditor_with_count]['industry'] = ncode
        data_object_results[key][creditor_with_count]['nature_of_claim'] = nature_claim
        data_object_results[key][creditor_with_count]['unsecured_claim_value'] = unsecured_claim_value.replace("$","").replace(",","")
        data_object_results[key][creditor_with_count]['creditor_company_name'] = comp_name
        data_object_results[key][creditor_with_count]['creditor_company_state'] = address_object[2]
        data_object_results[key][creditor_with_count]['creditor_company_zip'] = address_object[3]

    return(data_object_results)

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
        logger.warning(f'Detect Document Text Failed {documentName}: {e}')
        pass

    return my_list

def get_naics_code(my_list, dn):
    #naics_industry_codes = {'11': 'Agriculture, Forestry, Fishing and Hunting', '21': 'Mining', '22': 'Utilities', '23': 'Construction', '31': 'Manufacturing','32': 'Manufacturing','33': 'Manufacturing','42': 'Wholesale Trade','44': 'Retail Trade','45': 'Retail Trade','48': 'Transportation and Warehousing','49': 'Transportation and Warehousing','51': 'Information','52': 'Finance and Insurance','53': 'Real Estate Rental and Leasing','54': 'Professional, Scientific, and Technical Services','55': 'Management of Companies and Enterprises','56': 'Administrative and Support and Waste Management and Remediation Services','61': 'Educational Services','62': 'Health Care and Social Assistance','71': 'Arts, Entertainment, and Recreation','72': 'Accommodation and Food Services','81': 'Other Services (except Public Administration)','92': 'Public Administration'}
    logger.info("Parsing NAICS code...")
    r = re.compile("^(c\. naics.+)")
    ncde = 0
    find_naics_line = list(filter(r.match, my_list))
    if find_naics_line:
        naics_code = find_adjacents(str(find_naics_line[0]), my_list)
        logger.debug(naics_code)
        remove_space_naics_code = [(x.replace(' ','')) for x in naics_code]
        n_code = list(filter(lambda v: match('[0-9]{2,6}', v), remove_space_naics_code))
        if n_code:
            ncde = str(n_code[0])
            logger.debug('Found NAICS: ' + ncde)
            return ncde
        else:
            return None
    else:
        logger.warning('Unable to parse NAICS code: ' + dn)

def main():
    # If ASG supplied as cli arg
    get_naics_code('myl', 'dn')
    if args.convert_pdf:
        convert_pdf2png(args.convert_pdf)
    elif args.parse_png:
        tabledata_pdffromimage(args.parse_png)

# MAIN
if __name__ == '__main__':
    main()