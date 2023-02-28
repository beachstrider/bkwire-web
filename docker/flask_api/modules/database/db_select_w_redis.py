#!/usr/bin/python

import re
import os
import time
import redis
import json
import pyodbc
import pickle
import hashlib
import requests
import logging.config
from os import path
from datetime import datetime
import argparse
import mysql.connector
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from time import strptime


## Set up logging
log_file_path = path.join(path.dirname(path.abspath(__file__)), '/app/logging/logging.ini')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)
logger_list = ['boto', 'boto3', 'chardet', 'urllib3', 'botocore', 's3transfer', 'PIL']
for i in logger_list:
    logging.getLogger(i).setLevel(logging.CRITICAL) #sets all #logging sources to crit level

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
        self.redis_cache = redis.Redis(host=os.environ['REDIS_DB_HOST'], port=6379)

    def db_login(self):
        try:
            conn = mysql.connector.connect(
            user=self.mysql_db_user,
            password=self.mysql_db_password,
            host=self.mysql_db_host,
            database=self.mysql_db_database,
            auth_plugin='mysql_native_password')
        except Exception as e:
            logging.error(e)
            conn = None

        self.db_cnxn = conn

    def fetch(self, sql):
        hash = hashlib.sha256(sql.encode('utf-8')).hexdigest()
        hash_key = "sql_cache: " + hash
        logging.debug("Created key: %s" % hash_key)

        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            if self.redis_cache.get(hash_key):
                logging.debug('This was returned from redis')
                cache_result = pickle.loads(self.redis_cache.get(hash_key))
                return(cache_result)
            else:
                cursor.execute(sql)
                data = cursor.fetchall()
                self.redis_cache.set(hash_key, pickle.dumps(data))
                self.redis_cache.expire(hash_key, '3600')
                logging.debug('Cache key set and return mysql data')
                query_result = pickle.loads(self.redis_cache.get(hash_key))
                return (query_result)
        except Exception as e:
            logging.error(e)
            return(None)

    def fetch_no_cache(self, sql):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            logging.debug('return mysql data no cache')
            return (data)
        except Exception as e:
            logging.error(e)
            return(None)

    def sql_commit(self, sql):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            self.db_cnxn.commit()
            return('Success')
        except Exception as e:
            logging.error(e)
            return('Failed')

    def create(self, kwargs):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            sql = """INSERT INTO users (first_name, last_name, email_address, phone_number, company_name, company_address, company_zip_code, email_alerts_enabled, email_alert_1, email_alert_2, email_alert_3, text_alerts_enabled, phone_alert_1, phone_alert_2, phone_alert_3)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            val = [(kwargs['first_name'], kwargs['last_name'], kwargs['email_address'], kwargs['phone_number'], kwargs['company_name'], kwargs['company_address'], kwargs['company_zip_code'], kwargs['email_alerts_enabled'], kwargs['email_alert_1'], kwargs['email_alert_2'], kwargs['email_alert_3'], kwargs['text_alerts_enabled'], kwargs['phone_alert_1'], kwargs['phone_alert_2'], kwargs['phone_alert_3'])]
            cursor.executemany(sql, val)
            self.db_cnxn.commit()
            logging.debug('User creation successful')
            return('Success')
        except Exception as e:
            logging.error(e)
            return('Failed')

    #MOVED THIS TO JINJA2 template
    #def update(self, first_name=None, last_name=None, email_address=None, phone_number=None, company_name=None, company_address=None, company_zip_code=None, email_alerts_enabled=None, email_alert_1=None, email_alert_2=None, email_alert_3=None, text_alerts_enabled=None, phone_alert_1=None, phone_alert_2=None, phone_alert_3=None):
    def update(self, kwargs):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            sql = """UPDATE users
            SET (first_name, last_name, email_address, phone_number, company_name, company_address, company_zip_code, email_alerts_enabled, email_alert_1, email_alert_2, email_alert_3, text_alerts_enabled, phone_alert_1, phone_alert_2, phone_alert_3)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            val = [(kwargs['first_name'], kwargs['last_name'], kwargs['email_address'], kwargs['phone_number'], kwargs['company_name'], kwargs['company_address'], kwargs['company_zip_code'], kwargs['email_alerts_enabled'], kwargs['email_alert_1'], kwargs['email_alert_2'], kwargs['email_alert_3'], kwargs['text_alerts_enabled'], kwargs['phone_alert_1'], kwargs['phone_alert_2'], kwargs['phone_alert_3'])]
            cursor.executemany(sql, val)
            self.db_cnxn.commit()
            logging.debug('User creation successful')
            return('Success')
        except Exception as e:
            logging.error(e)
            return('Failed')

    def flush_cache(self):
        self.redis_cache.flushall()

#UPDATE Customers
#SET ContactName = 'Alfred Schmidt', City= 'Frankfurt'
#WHERE CustomerID = 1;
####################################################

def main():
    db1 = dbSelectItems()
    db1.db_login()
    if db1.db_cnxn != None:
        #my_query_result,my_num = db1.fetch("SELECT * FROM companies")
        db1.flush_cache()
    else:
        pass
    db1.db_cnxn.close()


# MAIN
if __name__ == '__main__':
    main()
