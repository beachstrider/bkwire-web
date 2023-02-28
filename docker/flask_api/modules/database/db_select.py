#!/usr/bin/python

import os
import pyodbc
import logging.config
from logtail import LogtailHandler
from os import path
from datetime import datetime
import mysql.connector


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
            logger.error(f"MySQL DB Login Failed: {e}")
            conn = None
        self.db_cnxn = conn

    def fetch_no_cache(self, sql):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
        except Exception as e:
            logger.error(f"fetch_no_cache: {e}, {sql}")
            data = None
        finally:
            cursor.close()
            return data

    def fetch_execute(self, sql, var):
        cursor = self.db_cnxn.cursor(dictionary=True)
        var = f"%{var}%"
        try:
            cursor.execute(sql, [var])
            data = cursor.fetchall()
            logger.debug('return mysql sani data no cache')
        except Exception as e:
            logger.error(f"MySQL fetch_execute FAILED: {e}")
            logger.debug(f"fetch_execute FAILED query: {sql}")
            data = None
        finally:
            cursor.close()
            return data


    def fetch_execute_v2(self, sql, var):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.execute(sql, [var])
            data = cursor.fetchall()
            logger.debug('return mysql sani data no cache')
        except Exception as e:
            logger.error(f"MySQL fetch_execute_v2 FAILED: {e}")
            logger.debug(f"fetch_execute_v2 FAILED query: {sql}")
            data = None
        finally:
            cursor.close()
            return data

    def sql_commit(self, sql):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            self.db_cnxn.commit()
            
            msg = 'Success'
        except Exception as e:
            logger.error(f"MySQL sql_commit Failed: {sql}: {e}")
            msg = 'Failed'
        finally:
            return msg

    def sql_transaction(self, sql):
        #logger.debug(sql)
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            return('Success')
        except Exception as e:
            logger.error(e)
            return('Failed')

    def sql_commit_w_values(self, sql, vals):
        """
        This module expects the 
        sql = "INSERT INTO bankruptcy_204206_data (creditor_name, creditor_zip) VALUES (%s,%s)"
        vals = (cred_title_comp, unsecured_creditor_zip)
        """
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.execute(sql, vals)
            self.db_cnxn.commit()
            return('Success')
        except Exception as e:
            logger.error(f"MySQL sql_commit_w_values Failed: {sql}: {e}")
            return('Failed')

    def sql_commit_many(self, sql, data):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            cursor.executemany(sql, data)
            self.db_cnxn.commit()
            return('Success')
        except Exception as e:
            logger.error(e)
            self.db_cnxn.rollback()
            return('Failed')

    def create(self, kwargs):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            sql = """INSERT INTO users (first_name, last_name, email_address, phone_number, company_sector, company_name, company_state, company_zip_code, email_alerts_enabled, email_alert_1, email_alert_2, email_alert_3, text_alerts_enabled, phone_alert_1, phone_alert_2, phone_alert_3)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            val = [(kwargs['first_name'], kwargs['last_name'], kwargs['email_address'], kwargs['phone_number'], kwargs['company_sector'], kwargs['company_name'], kwargs['company_state'], kwargs['company_zip_code'], kwargs['email_alerts_enabled'], kwargs['email_alert_1'], kwargs['email_alert_2'], kwargs['email_alert_3'], kwargs['text_alerts_enabled'], kwargs['phone_alert_1'], kwargs['phone_alert_2'], kwargs['phone_alert_3'])]
            cursor.executemany(sql, val)
            self.db_cnxn.commit()
            logger.debug('User creation successful')
            return('Success', cursor.lastrowid)
        except Exception as e:
            logger.error(e)
            return(e)

    def create_team_user(self, pemail, memail):
        cursor = self.db_cnxn.cursor(dictionary=True)
        try:
            sql = """INSERT INTO user_team (principal_email_address, member_email_address)
            VALUES (%s,%s)"""
            val = [(pemail, memail)]
            cursor.executemany(sql, val)
            self.db_cnxn.commit()
            logger.debug('Team user creation successful')
            return('Team user creation successful')
        except Exception as e:
            logger.error(f"Team user creation failed: {e}")
            return(f"Team user creation failed: {e}")
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
            logger.debug('User creation successful')
            return('Success')
        except Exception as e:
            logger.error(e)
            return('Failed')

    def sql_truncate(self, sql_table):
        logger.debug(sql_table)
        cursor = self.db_cnxn.cursor(dictionary=True)
        sql = f"TRUNCATE TABLE {sql_table}"
        try:
            cursor.execute(sql)
            self.db_cnxn.close()
            return('Success')
        except Exception as e:
            logger.error(e)
            return('Failed')

    def sql_delete_team_user(self, pemail, memail):
        cursor = self.db_cnxn.cursor(dictionary=True)
        sql = f"DELETE FROM user_team WHERE principal_email_address = \'{pemail}\' AND member_email_address = \'{memail}\'"
        sql_user_table = f"UPDATE users SET subscription_id=NULL, subscription_price_id=NULL, subscription_status=NULL, \
            subscription_inherited=0, subscription_level=0 WHERE email_address = \'{memail}\'"
        #DELETE FROM sql_table WHERE condition;
        try:
            cursor.execute(sql)
            cursor.execute(sql_user_table)
            self.db_cnxn.commit()
            self.db_cnxn.close()
            return('Removed team member successfully')
        except Exception as e:
            logger.error(e)
            return('Removed team member failed')
#UPDATE Customers
#SET ContactName = 'Alfred Schmidt', City= 'Frankfurt'
#WHERE CustomerID = 1;
####################################################

def main():
    db1 = dbSelectItems()
    db1.db_login()
    if db1.db_cnxn != None:
        #my_query_result,my_num = db1.fetch("SELECT * FROM companies")
        #db1.flush_cache()
        sql ="""SELECT * FROM companies WHERE name like %s"""
        comp = 'amc'
        print(db1.fetch_execute(sql, comp))
    else:
        pass
    db1.db_cnxn.close()


# MAIN
if __name__ == '__main__':
    main()
