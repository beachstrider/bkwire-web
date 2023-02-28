#!/usr/bin/python

import re
import os
import sys
import boto3
import logging.config
from logtail import LogtailHandler
from os import path
from datetime import datetime
import argparse
import mysql.connector
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

## IMPORT CUSTOM MODULES ##
sys.path.insert(0, '/app')
from modules.address.international_parser import IntAddyParse
from modules.database.db_connec_v2 import db_login, insert_data_bfd, insert_data_dci, \
insert_data_b201d, insert_data_b204206d, insert_companies, insert_company_ein
import bkw_daily_import

#Setup flags here
parser = argparse.ArgumentParser(
    description='Import Creditor Data tied to case in our system',
    epilog='Example: python man_creditors.py')

parser.add_argument("-f",
                    "--file",
                    dest='cfile',
                    help="The file to import",
                    required=False)

# Parse CLI ARGS/usr/bin/docker exec -t flask-api python daily_import_v3.py -s '2022-05-10' -e '2022-05'11'
args = parser.parse_args()


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

now = datetime.now()
db_ts = now.strftime('%Y/%m/%d')
config_create_date = now.strftime('%Y%d%m%H%M%S')
xmlDict = {}

#################### NEW 2.0 ############################

class dbSelectItems:
    def __init__(self):
        self.mysql_db_user = os.environ['MYSQL_DB_USER']
        self.mysql_db_password = os.environ['MYSQL_DB_PASSWORD']
        self.mysql_db_host = os.environ['MYSQL_DB_HOST']
        self.mysql_db_database = os.environ['MYSQL_DB_DATABASE']

    def db_login(self):
        try:
            conn = mysql.connector.connect(
            user=self.mysql_db_user,
            password=self.mysql_db_password,
            host=self.mysql_db_host,
            database=self.mysql_db_database,
            auth_plugin='mysql_native_password')
        except Exception as e:
            logger.error(e)
            conn = None

        self.db_cnxn = conn

    def fetch_no_cache(self, sql):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            logger.debug('return mysql data no cache')
            return (data)
        except Exception as e:
            logger.error(e)
            return(None)

    def sql_commit(self, sql):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            self.db_cnxn.commit()
            return('Success')
        except Exception as e:
            logger.error(e)
            return('Failed')

class awsS3transfer:
    def __init__(aself):
        aself.aws_key = os.environ['AWS_ACCESS_KEY_ID']
        aself.aws_secret = os.environ['AWS_SECRET_ACCESS_KEY']
        aself.mysql_bucket = 'prd-bkwire-db-backup'
        aself.mysql_db_database = os.environ['MYSQL_DB_DATABASE']
        aself.filename = 'companies.csv'

    def download_backup_from_s3(aself):
        # Upload the file
        print("[+] Downloading S3 File")
        s3_client = boto3.client('s3', aws_access_key_id=aself.aws_key, aws_secret_access_key=aself.aws_secret)
      
        file_name = aself.filename
        obj_name = file_name
        try:
            s3_client.download_file(aself.mysql_bucket, obj_name, file_name)
        except Exception as e:
            print(e)
            return False
        print("[+] Complete")

        return True


def main():

    dbs = dbSelectItems()
    dbs.db_login()
    iap = IntAddyParse()
    presults = {}

    as3 = awsS3transfer()
    as3.download_backup_from_s3()
    
    with open('companies.csv') as f:
        lines = f.readlines()
        lines.pop(0)
        for l in lines:
            no_quote_string = l.strip().replace('\"', '')
            ldcompany_object = no_quote_string.split('::')
            # Run Address Parser
            address_object = iap.parse_address(ldcompany_object[0])
            if address_object[0] == None:
                comp_string = no_quote_string.split()
                try:
                    comp_name = f"{comp_string[0]} {comp_string[1]}"
                except:
                    comp_name = ldcompany_object[0]
            else:
                comp_name = address_object[0].strip()
            try:
                ind_num = ldcompany_object[8]
            except:
                ind_num = 0
            insert_companies(dbs.db_cnxn, comp_name, ind_num)
            bfid = dbs.fetch_no_cache(f"SELECT id FROM `bankruptcy_filing_data` WHERE dci_id = {ldcompany_object[7]};")
            insert_data_b204206d(dbs.db_cnxn, comp_name, address_object[3], ldcompany_object[2], ldcompany_object[6], ldcompany_object[8], bfid[0]['id'])
            # run through 204 notify logic
            #unsecured_creditor_name, unsecured_creditor_zip, unsecured_creditor_nature_of_claim, unsecured_creditor_claim_value, unsecured_creditor_industry, case_filing_id
            key = ldcompany_object[7]
            presults[key] = {}
            presults[key]['dci_id'] = key
            presults[key]['parse_204206_attempt'] = True
    # check_missing_204_data
    bkw_daily_import.check_missing_204_data(presults)


# MAIN
if __name__ == '__main__':
    main()