#!/usr/bin/python
import os,sys
import re
import time
import datetime
import argparse
from os import path
import logging.config
from logtail import LogtailHandler
from datetime import date
from datetime import timedelta
## IMPORT CUSTOM MODULES ##
sys.path.insert(0, '/app')
from sub_apps.bkw_notifications_v2 import CaseNotify
from sub_apps.industry_updater import UpdateIndustry
from modules.database.db_select import dbSelectItems
from sub_apps.bkw_app_api_funcs import build_pacer_data_from_sql, check_missing_204_data, pacer_login_session, parse_pacer_results


# GET Datetime NOW
now  = datetime.datetime.now()
config_create_date = now.strftime('%Y%d%m%H%M%S')

# Set up dates as needed for search
today = date.today().strftime('%Y-%m-%d')
first_of_year = date(date.today().year, 1, 1)
first_of_year = first_of_year.strftime('%m/%d/%Y')
yesterday = date.today() - timedelta(days = 1)
yesterday = yesterday.strftime('%Y-%m-%d')


#Setup flags here
parser = argparse.ArgumentParser(
    description='Daily Pacer Download Service',
    epilog='Example: python daily_import_v3.py')

parser.add_argument("-s",
                    "--date-filed-start",
                    dest='dfs',
                    help="The Filed Start Date - format YYYY-MM-DD",
                    required=False,
                    type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date())

parser.add_argument("-e",
                    "--date-filed-end",
                    dest='dfe',
                    help="The Filed End Date - format YYYY-MM-DD",
                    required=False,
                    type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date())

parser.add_argument("--case-recheck",
                    dest='crc',
                    help="Case recheck flag(Query all missing 204 data)",
                    required=False,
                    action='store_true')

parser.add_argument("--case-recheck-mvp",
                    dest='crcmvp',
                    help="Case recheck flag(Query all missing 204 data) for MVP Users",
                    required=False,
                    action='store_true')                    

parser.add_argument("--industry-updater",
                    dest='indu',
                    help="Trigger Industry Updater Service",
                    required=False,
                    action='store_true')

parser.add_argument("--no-batch-search",
                    dest='nbs',
                    help="Disable PACER batch search (will use json_case_data file)",
                    required=False,
                    action='store_true')

parser.add_argument("--run-daily-loss",
                    dest='rdl',
                    help="Run the daily loss notification service",
                    required=False,
                    action='store_true')
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


def batch_pacer_search(p1, start_filed, end_filed):
    batch_data = p1.pacer_case_search_batch(start_filed, end_filed)#2022-04-15
    time.sleep(15)
    r_status = p1.batch_report_status()
    try:
        count = 0
        while (len(r_status['content']) > count):
            if r_status['content'][count]['reportId'] == batch_data['reportId'] and r_status['content'][count]['status'] == 'COMPLETED':
                p1.batch_report_download(batch_data['reportId'])
            elif r_status['content'][count]['reportId'] == batch_data['reportId'] and r_status['content'][count]['status'] == 'RUNNING':
                time.sleep(15)
                r_status = p1.batch_report_status(batch_data['reportId'])
                if r_status['content'][count]['reportId'] == batch_data['reportId'] and r_status['content'][count]['status'] == 'COMPLETED':
                    p1.batch_report_download(batch_data['reportId'])
                else:
                    logger.error('Still running')
                    logger.debug(r_status)
                    exit(1)
            elif r_status['content'][count]['reportId'] == batch_data['reportId'] and r_status['content'][count]['status'] == 'FAILED':
                return('Failed')
            else:
                pass
            count += 1
    except Exception as e:
        logger.error(e)
        exit(1)

def query_for_missing_data_sets(member_status='BASIC'):
    db1 = dbSelectItems()
    db1.db_login()
    pacer_data_results = {}
    if member_status == 'MVP':
        sql_query = f"SELECT * FROM `bankruptcy_filing_data` \
            JOIN bankruptcies_watchlist ON bankruptcies_watchlist.did = bankruptcy_filing_data.dci_id \
            JOIN users ON users.id = bankruptcies_watchlist.user_id \
            WHERE bankruptcy_filing_data.status_204206 = 0 AND users.subscription_price_id = '{os.environ['STRIPE_MVP_PRICE_ID']}' \
            GROUP BY dci_id \
            ORDER BY `bankruptcy_filing_data`.`dci_id`"
    else:
        sql_query = f"SELECT * FROM `bankruptcy_filing_data` JOIN bankruptcies_watchlist ON bankruptcies_watchlist.did = bankruptcy_filing_data.dci_id WHERE bankruptcy_filing_data.status_204206 = 0 GROUP BY dci_id ORDER BY `bankruptcy_filing_data`.`dci_id`;"
    mysql_nodata_sets = db1.fetch_no_cache(sql_query)
    pacer_data_results = build_pacer_data_from_sql(mysql_nodata_sets)
    
    return pacer_data_results

def run_ind_updater():    #RUN industry Updater
    logger.info('Running industry updater')
    ui = UpdateIndustry()
    ui.runit()

def run_not_todays_loss():
    logger.info('Running daily loss notifications')
    cn = CaseNotify()
    cn.notify_todays_loss_company()

def main():
    # PACER API SERVICE
    logger.info('Script Starting...')
    status = None
    p1, p2 = pacer_login_session()
    if args.crc:
        results = query_for_missing_data_sets()
        parsed_pacer_results = parse_pacer_results(p1, p2, results)
        check_missing_204_data(parsed_pacer_results)
        exit(0)
    elif args.crcmvp:
        results = query_for_missing_data_sets(member_status='MVP')
        parsed_pacer_results = parse_pacer_results(p1, p2, results)
        check_missing_204_data(parsed_pacer_results)
        exit(0)        
    elif args.dfs and args.dfe:
        logger.info('Running batch search for dates: ' + str(args.dfs) +' ' +str(args.dfe))
        if args.nbs:
            status = None
        else:
            status = batch_pacer_search(p1, start_filed=str(args.dfs), end_filed=str(args.dfe))
        if status == 'Failed':
            logger.warning("Pacer batch search failed - Zzzz 60 and retry")
            time.sleep(60)
            stat2 = batch_pacer_search(p1, start_filed=str(args.dfs), end_filed=str(args.dfe))
            if stat2 == 'Failed':
                logger.error("Pacer batch failed x2!")
                exit(1)
        p1.pacer_data_from_file()
        p1.pcl_parse_json()
        pacer_data_results = p1.build_pacer_case_search_data_results()
        parse_pacer_results(p1, p2, pacer_data_results)

    elif args.rdl:
        logger.info('Running daily loss notifications')
        cn = CaseNotify()
        cn.notify_todays_loss_company()
        exit(0)
    elif args.indu:
        run_ind_updater()
        exit(0)

    logger.info('Daily Import Script Completed')
    exit(0)


# MAIN
if __name__ == '__main__':
    main()
