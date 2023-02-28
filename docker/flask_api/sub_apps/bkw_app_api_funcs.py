import re
import json
import time
import requests
import os, glob, sys
from os import path
import pandas as pd
import logging.config
from logtail import LogtailHandler
import shortuuid
import pandas as pd
from datetime import datetime, timedelta, date
from jinja2 import Environment, FileSystemLoader
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

## IMPORT CUSTOM MODULES ##
sys.path.insert(0, '/app')
from sub_apps.bkw_notifications_v2 import CaseNotify
from modules.pacer.pacer_api_v3 import PacerApiSvc
from modules.bkwdatetime.date_time import BkwDateTime
from sub_apps.bkw_app_email import BkAppEmailFunctions
from modules.database.db_select import dbSelectItems
from modules.notifications.sns_topics import SNSTopic
from modules.notifications.bkw_constantcontact import ConstantContact
from modules.parsers.parse_results_download_pdf_v2 import ResultsParserSvc
from modules.aws.check_s3_objects import check_against_s3_objects
from modules.aws.textrac_v3 import convert_pdf2png, rawtext_pdffromimage, \
get_naics_code, parse_201, parse_204, parse_205, parse_206, delete_file, copy_object, upload_file
from modules.database.db_connec_v2 import db_login, insert_data_bfd, insert_data_dci, \
insert_data_b201d, insert_data_b204206d, insert_companies, insert_company_ein, \
insert_docket_data, insert_data_additional_info, insert_files_inventory, insert_purchases, \
update_data_bfd, company_scrub, title, insert_docket_entry_file, doc_table_get_id, doc_entry_file_link_table_id
from sub_apps import bkw_app_api_config

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

def pacer_login_session():
    logger.debug(f"pacer_login_session triggered")
    p1 = PacerApiSvc()
    pacer_login_session = None
    cookie_check = p1.pacer_check_cookie()
    logger.debug(f"cookie_check: {cookie_check}")
    if cookie_check == 'expired':
        logger.debug('PCL: cookies expired')
        pacer_login_session = p1.pacer_session_login()
        logger.debug(f"pacer_login_session: {pacer_login_session}")
        p1.pacer_cso_login()
    else:
        logger.debug('PCL: cookies still valid')
        pacer_login_session = cookie_check

    if pacer_login_session == None:
        logger.error(f"PACER login session failed: {pacer_login_session}")
        exit(1)
    p2 = ResultsParserSvc(pacer_login_session)
    return(p1, p2)

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

def get_daily_time():
    date_today = date.today()
    if date.today().weekday() == 0:
        date_previous = date_today - timedelta(days = 3)
    else:
        date_previous = date_today - timedelta(days = 1)

    today_month = datetime.now().strftime(("%b"))
    today_day = datetime.now().strftime(("%d"))
    return(date_today, date_previous, today_month, today_day)

def get_weekly_time():
    date_today = date.today()
    date_previous = date_today - timedelta(days = 7)
    return(date_today, date_previous)

def get_bi_weekly_time():
    date_today = date.today()
    date_previous = date_today - timedelta(days = 14)
    return(date_today, date_previous)

def gen_presigned_url(bucket_name, object_key, responsectype='application/pdf', expiry=600):
    client = boto3.client("s3",region_name='us-west-2')
    try:
        response = client.generate_presigned_url('get_object',
                                                  Params={'Bucket': bucket_name,'Key': object_key, 'ResponseContentDisposition': 'inline; filename=' + object_key, 'ResponseContentType': responsectype},
                                                  ExpiresIn=expiry)
        return(response)
    except ClientError as e:
        logger.error(e)

def download_docket_from_s3_archive(bucket_name, object_key):
    s3 = boto3.client('s3')

    try:
        obj = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = obj["Body"].read().decode('utf-8')
    except Exception as e:
        logger.error(e)
        return False

    return (file_content)

def industries():
    """
    This function responds to a request for /pyapi/industries
    with the selected DB data results returned for all defined industries

    :return:        Database Query Results Dictionary
    """
    db1 = dbSelectItems()
    db1.db_login()
    if db1.db_cnxn != None:
        my_query_result = db1.fetch_no_cache("SELECT id, naics_desc FROM industry_desc ORDER BY naics_desc")
        return(my_query_result, 200)
    else:
        return('Query Failed', 500)
    db1.db_cnxn.close()

def bk_graph():
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_view_bk_30_day')
    output = template.render()
    sql_results = run_sql_queries_no_cache(output)
    new_dlist = []
    return_list = []
    datelist = pd.date_range(end = (date.today() - timedelta(days = 1)), periods = 30).to_pydatetime().tolist()
    for d in datelist:
        dsplit = str(d).split()
        new_dlist.append(dsplit[0])
    for nd in new_dlist:
        myl = list(filter(lambda df_sqlr: df_sqlr['date_filed'] == nd, sql_results[0]))
        if myl:
            return_list.append(myl[0])
        else:
            entry = {'count': 0, 'date_filed': nd}
            return_list.append(entry)
    return(return_list)

def list_splash():
    date_today = date.today()
    date_yesterday = date_today - timedelta(days = 3)
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_loss_splash')
    output = template.render(today_date=date_yesterday)
    result = run_sql_queries_no_cache(output)
    return(result)

def list_bankruptcies(guid, **kwargs):
    """
    This function responds to a request for /pyapi/list_bankruptcies
    with the selected DB data results returned for all bankruptcies joined data

    :return:        Database Query Results Dictionary
    """
    bk_filters = []
    bk_filters_asset = []
    bk_filters_chapter = []
    bk_filters_creditor = []
    bk_filters_liability = []
    bk_filters_industries = []
    bk_filters_involuntary = []
    bk_filters_sub_chapv = []
    start_date_filed, end_date_filed = None, None
    start_date_added, end_date_added = None, None
    city, state_code, inv_status, sub_chapv = None, None, None, None
    #logger.debug(f"List BKs KWARGS: {kwargs}")
    kwargs['offset'] = (int(kwargs['page'][0]) - 1) * int(kwargs['page_size'][0])
    try:
        if kwargs['search'][0] == None:
            pass
        else:
            quote_val = kwargs['search'][0]
            bk_filters.append({'key': 'case_name', 'val': quote_val})
    except:
        pass

    try:
        if kwargs['industries'] == 0:
            pass
        else:
            for i in kwargs['industries']:
                bk_filters_industries.append({'key': 'industry_desc.id', 'val': i})
    except:
        pass
    try:
        if kwargs['chapter_types'] == 0:
            pass
        else:
            for i in kwargs['chapter_types']:
                bk_filters_chapter.append({'key': 'cs_chapter', 'val': i})
    except:
        pass
    try:
        if 'involuntary' in kwargs:
            if kwargs['involuntary'][0] == 'true':
                inv_status = 1
            else:
                inv_status = 0
        else:
            pass     
    except:
        pass
    try:
        if 'sub_chapv' in kwargs:
            if kwargs['sub_chapv'][0] == 'true':
                sub_chapv = 1
            else:
                sub_chapv = 0
        else:
            pass     
    except:
        pass    
    try:
        if kwargs['creditor_ranges'] == 0:
            pass
        else:
            for i in kwargs['creditor_ranges']:
                bk_filters_creditor.append({'key': 'estimated_creditors.id', 'val': i})
    except:
        pass
    try:
        if kwargs['asset_ranges'] == 0:
            pass
        else:
            for i in kwargs['asset_ranges']:
                bk_filters_asset.append({'key': 'estimated_assets.id', 'val': i})
    except:
        pass

    try:
        if kwargs['liability_ranges'] == 0:
            pass
        else:
            for i in kwargs['liability_ranges']:
                bk_filters_liability.append({'key': 'estimated_liabilities.id', 'val': i})
    except:
        pass

    try:
        if kwargs['start_date_filed'][0] == None:
            pass
        else:
            start_date_filed = kwargs['start_date_filed'][0]
            end_date_filed = kwargs['end_date_filed'][0]
    except:
        pass

    try:
        if kwargs['start_date_added'][0] == None:
            pass
        else:
            start_date_added = kwargs['start_date_added'][0]
            end_date_added = kwargs['end_date_added'][0]
    except:
        pass

    try:
        if kwargs['city'][0] == None:
            pass
        else:
            city = kwargs['city'][0]
    except:
        pass

    try:
        if kwargs['state_code'][0] == None:
            pass
        else:
            state_code = kwargs['state_code'][0]
    except:
        pass

    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_bk_query_filter')
    output = template.render(kwargs=kwargs, bk_filters=bk_filters, bk_filters_asset=bk_filters_asset, \
    bk_filters_chapter=bk_filters_chapter, bk_filters_creditor=bk_filters_creditor, bk_filters_liability=bk_filters_liability, \
    bk_filters_industries=bk_filters_industries, sdf=start_date_filed, edf=end_date_filed, sda=start_date_added, eda=end_date_added, \
    city=city, sc=state_code, bk_uid=guid, inv_status=inv_status, sub_chapv=sub_chapv)

    query_drop_line = "\n".join(output.split("\n")[:-3])
    query_count = re.sub(r'(SELECT).*(FROM)', r'SELECT COUNT(*) as result_count FROM', query_drop_line, flags=re.DOTALL | re.M)
    fix_query_count = re.sub(r'GROUP BY', r'ORDER BY', query_count, flags=re.DOTALL | re.M)
    #logger.debug(f"MySQL list_bankruptcies: {output}")
    return(run_sql_queries_no_cache(output, fix_query_count))

def list_losses(guid, **kwargs):
    """
    This function responds to a request for /pyapi/list_bankruptcies
    with the selected DB data results returned for all bankruptcies joined data

    :return:        Database Query Results Dictionary
    """
    naics_filters = []
    loss_filters_dc_id = []
    loss_filters_search = []
    loss_filters_unsecured_values = []
    city, state_code = None, None
    template, query_count = None, None
    start_date_added, end_date_added = None, None
    start_date_filed, end_date_filed = None, None
    #logger.debug(f"List Loss KWARGS: {kwargs}")
    kwargs['offset'] = (int(kwargs['page'][0]) - 1) * int(kwargs['page_size'][0])
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    max_r = False

    try:
        if kwargs['loss'][0] == 0 and kwargs['loss'][1] == 0:
            pass
        else:
            loss_filters_unsecured_values.append({'key': 'unsecured_claim_min', 'val': kwargs['loss'][0], 'sign': '>'})
            loss_filters_unsecured_values.append({'key': 'unsecured_claim_max', 'val': kwargs['loss'][1], 'sign': '<'})
    except Exception as e:
        pass

    try:
        if kwargs['search'][0] == None:
            pass
        else:
            quote_val = kwargs['search'][0]
            loss_filters_search.append({'key': 'creditor_name', 'val': quote_val})
    except:
        pass

    try:
        if len(kwargs['industries']) == 0:
            pass
        else:
            for i in kwargs['industries']:
                naics_filters.append({'key': 'companies.industry_id', 'val': i})
    except:
        pass

    try:
        if kwargs['id'][0] == None:
            pass
        else:
            quote_val = kwargs['id'][0]
            loss_filters_dc_id.append({'key': 'dc_id', 'val': quote_val})
    except:
        pass

    try:
        if kwargs['max_losses_per_case'][0] == None:
            pass
        else:
            max_r = True
            kwargs['umax_results'] = [kwargs['max_losses_per_case'][0]]
    except:
        pass

    try:
        if kwargs['start_date_filed'][0] == None:
            pass
        else:
            start_date_filed = kwargs['start_date_filed'][0]
            end_date_filed = kwargs['end_date_filed'][0]
    except:
        pass

    try:
        if kwargs['start_date_added'][0] == None:
            pass
        else:
            start_date_added = kwargs['start_date_added'][0]
            end_date_added = kwargs['end_date_added'][0]
    except:
        pass

    try:
        if kwargs['city'][0] == None:
            pass
        else:
            city = kwargs['city'][0]
    except:
        pass

    try:
        if kwargs['state_code'][0] == None:
            pass
        else:
            state_code = kwargs['state_code'][0]
    except:
        pass

    if max_r == True:
        template = env.get_template('mysql_loss_query_filter_v2')
        output = template.render(kwargs=kwargs, loss_filters_search=loss_filters_search, naics_filters=naics_filters, \
        loss_filters_unsecured_values=loss_filters_unsecured_values, loss_filters_dc_id=loss_filters_dc_id, \
        sdf=start_date_filed, edf=end_date_filed, sda=start_date_added, eda=end_date_added, city=city, sc=state_code, bk_uid=guid)
        query_count = re.sub(r'SELECT \* FROM myCTE', r'SELECT COUNT(*) as result_count FROM myCTE', output, flags=re.DOTALL | re.M)
    else:
        template = env.get_template('mysql_loss_query_filter')
        output = template.render(kwargs=kwargs, loss_filters_search=loss_filters_search, naics_filters=naics_filters, \
        loss_filters_unsecured_values=loss_filters_unsecured_values, loss_filters_dc_id=loss_filters_dc_id, \
        sdf=start_date_filed, edf=end_date_filed, sda=start_date_added, eda=end_date_added, city=city, sc=state_code, bk_uid=guid)
        query_drop_line = "\n".join(output.split("\n")[:-3])
        query_count = re.sub(r'(SELECT).*(FROM)', r'SELECT COUNT(*) as result_count FROM', query_drop_line, flags=re.DOTALL | re.M)
    return (run_sql_queries_no_cache(output, query_count))

def header_search(**kwargs):
    logger.debug(f"Header Search KWARGS: {kwargs}")
    kwargs['umax_results'] = [1]
    kwargs['page_size'] = [kwargs['max_results'][0]]
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_loss_query_filter_search_v2')
    output = template.render(kwargs=kwargs)

    kwargs['sort_column'] = ['case_name']
    template2 = env.get_template('mysql_bk_query_filter_search_v2')
    output2 = template2.render(kwargs=kwargs)

    rsq1 = run_sql_queries_no_cache_v2(output, kwargs['search'][0])
    rsq2 = run_sql_queries_no_cache_v2(output2, kwargs['search'][0])
    bankruptcies,losses = [rsq2[0]],[rsq1[0]]

    page_info = {
                'bankruptcies': bankruptcies[0], # all the response items will go in this array
                'losses': losses[0], # current page
    }
    return(page_info, 200)

def create_team_user(**kwargs):
    logger.debug(f"Create Team KWARGS: {kwargs}")
    db1 = dbSelectItems()
    # Create BKWire User
    db1.db_login()
    get_user_res = get_user(kwargs['userid'])
    #check if member_email already has a subscription
    if kwargs['member_email_address'] == get_user_res[0][0]['email_address']:
        return(f"Team leader can not be Team member") 
    
    #check subscription
    if get_user_res[0][0]['subscription_price_level'] == bkw_app_api_config.team_level:
        sql_count = f"SELECT count(*) as Count FROM user_team WHERE principal_email_address = \'{get_user_res[0][0]['email_address']}\'"
        sqlc_res = db1.fetch_no_cache(sql_count)
        if get_user_res[0][0]['max_team_count'] == 0:
            max_team_count = bkw_app_api_config.default_max_team_count
        else:
            max_team_count = get_user_res[0][0]['max_team_count']
        if sqlc_res[0]['Count'] < max_team_count:
            check_sub_sql = get_user_id(kwargs['member_email_address'])
            if check_sub_sql[0]:
                resp = get_user(check_sub_sql[0][0]['id'])
                if resp[0][0]['subscription_status'] == 'active' or resp[0][0]['subscription_id'] != None:
                    return(f"Subscription already exists for {kwargs['member_email_address']}")
                elif resp[0][0]['subscription_inherited'] == True:
                    return(f"User {kwargs['member_email_address']} is already a member of a team")
                else:
                    user_id = create_tuser_associated_stripe(first_name=None, last_name=None, phone_number=None, company_name=None, company_state=None, company_zip_code=None, email_alerts_enabled=True, email_alert_1=None, email_alert_2=None, email_alert_3=None, text_alerts_enabled=False, phone_alert_1=None, phone_alert_2=None, phone_alert_3=None, is_social=None, auth0=None, company_sector=None, email_address=kwargs['member_email_address'], subscription_id=get_user_res[0][0]['subscription_id'], subscription_status='active', subscription_price_id=get_user_res[0][0]['subscription_price_id'], subscription_inherited=1, customer_id=get_user_res[0][0]['customer_id'])
                    #Update user_team DB with new entry
                    update_user(user_id[1], subscription_id=get_user_res[0][0]['subscription_id'], subscription_status='active', subscription_price_id=get_user_res[0][0]['subscription_price_id'], subscription_inherited=1, customer_id=get_user_res[0][0]['customer_id'])
                    results = db1.create_team_user(get_user_res[0][0]['email_address'], kwargs['member_email_address'])
                    return(results)
            else:
                user_id = create_tuser_associated_stripe(first_name=None, last_name=None, phone_number=None, company_name=None, company_state=None, company_zip_code=None, email_alerts_enabled=False, email_alert_1=None, email_alert_2=None, email_alert_3=None, text_alerts_enabled=False, phone_alert_1=None, phone_alert_2=None, phone_alert_3=None, is_social=None, auth0=None, company_sector=None, email_address=kwargs['member_email_address'])
                #Update user_team DB with new entry
                update_user(user_id[1], subscription_id=get_user_res[0][0]['subscription_id'], subscription_status='active', subscription_price_id=get_user_res[0][0]['subscription_price_id'], subscription_inherited=1, customer_id=get_user_res[0][0]['customer_id'])
                results = db1.create_team_user(get_user_res[0][0]['email_address'], kwargs['member_email_address'])
                return(results)
        else:
            return(f"Team has reached max memberships")
    else:
        return 'Please update subscription to a Team Membership'

def delete_team_user(**kwargs):
    logger.debug(f"Delete Team KWARGS: {kwargs}")
    db1 = dbSelectItems()
    db1.db_login()
    get_user_res = get_user(kwargs['userid'])
    sqlm_res, sqlp_res = None, None
    # Delete BKWire Team User
    sql_princ_exists = f"SELECT * FROM user_team WHERE principal_email_address = '{get_user_res[0][0]['email_address']}'"
    sqlp_res = db1.fetch_no_cache(sql_princ_exists)
    if sqlp_res:
        sql_member_exists = f"SELECT * FROM user_team WHERE member_email_address = '{kwargs['member_email_address']}'"
        sqlm_res = db1.fetch_no_cache(sql_member_exists)
        if sqlm_res:
            res = db1.sql_delete_team_user(get_user_res[0][0]['email_address'], kwargs['member_email_address'])
            return(res)
        else:
            return(f"No user found on team {get_user_res[0][0]['email_address']}")
    else:
        return(f"No team found for user {kwargs['member_email_address']}")

def create_tuser_associated_stripe(**kwargs):
    logger.debug(f"Create Tuser Assoc. stripe KWARGS: {kwargs}")
    new_user_id = None
    db1 = dbSelectItems()
    cc = ConstantContact()
    # Create BKWire User
    db1.db_login()
    sql_user_exists = f"SELECT * FROM users WHERE email_address = '{kwargs['email_address']}'"
    sql_user_res = db1.fetch_no_cache(sql_user_exists)
    #Send Team Member Email HERE#
    BKAEF = BkAppEmailFunctions()
    BKAEF.build_campaign_email(sub_line='BKwire Team Membership',
                            camp_name=f"BKwire Team Membership - {kwargs['email_address']}",
                            email_address=[kwargs['email_address']],
                            list_name='BKwire Team Member List - recycle',
                            html_temp_name='bkw_team_member')    
    try:
        logger.debug(f"User already exists in users table: {kwargs['email_address']}")
        new_user_id = sql_user_res[0]['id']
    except:
        new_user_id_res = db1.create(kwargs)
        new_user_id = new_user_id_res[1]
        #Create Stripe Customer
        logger.debug(f"Creating new user: {kwargs['email_address']}")
        
        cd = {
            "email_address": kwargs['email_address'],
            "create_source": "Contact",
            "list_memberships": [
                "4f905538-0148-11ed-81cf-fa163ecbdd18"
            ]
        }
        cc.create_contact(cd)    

    return ('Team user created successfully', new_user_id)

def create_user(**kwargs):
    logger.debug(f"create_user triggered: {kwargs['email_address']}")
    db1 = dbSelectItems()
    # Create BKWire User
    db1.db_login()
    new_user_id = db1.create(kwargs)

    return (new_user_id[0], new_user_id[1])

def get_user(user_id):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_user_query_filter')
    output = template.render(user_id=user_id)
    results = run_sql_queries_no_cache(output)
    return(results)

def get_user_id(user_email):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_user_id_query')
    output = template.render(user_email=user_email)
    return(run_sql_queries_no_cache(output))

def update_user(guid, **kwargs):
    update_user_info = []
    logger.debug(f"APP API Funcs update_user: {kwargs}")
    for key, value in kwargs.items():
        if value == None:
            update_user_info.append({'key': key, 'val': 'null'})
        elif value == '':
            update_user_info.append({'key': key, 'val': 'null'})
        elif value == True or value == False or type(value) == int:
            update_user_info.append({'key': key, 'val': int(value)})
        elif value == 'true' or value == 'false':
            if value == 'true':
                value = 1
            elif value == 'false':
                value = 0
            update_user_info.append({'key': key, 'val': int(value)})        
        else:
            value = '\'' + value + '\''
            update_user_info.append({'key': key, 'val': value})

    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_user_update_info')
    output = template.render(user_id=guid, update_user_info=update_user_info)
    logger.debug(f"update_user output: {output}")
    create_user_constant_contact(guid, kwargs)
    return(run_sql_commit(output))
    
def create_user_constant_contact(guid, kwargs):
    ''' This will update the CC user if already exists '''
    logger.debug(f"create_user_constant_contact triggered")
    cd = None
    naics_value = ''
    cc_update_values = []
    db1 = dbSelectItems()
    db1.db_login()
    cc = ConstantContact()
    get_user_res = get_user(guid)
    value_add_list = bkw_app_api_config.user_values_add_cc

    for key, value in kwargs.items():
        if key in value_add_list and value != None:
            if 'company_sector' == key:
                sql_query = f"SELECT naics_desc FROM `industry_desc` WHERE id = {value}"
                naics_desc = db1.fetch_no_cache(sql_query)
                naics_value = naics_desc[0]['naics_desc']
            else:
                cc_update_values.append({'key': key, 'value': value})

    file_loader = FileSystemLoader('templates/cc')
    env = Environment(loader=file_loader)
    template = env.get_template('constant_contact_user_update')
    output = template.render(user_attributes=cc_update_values, naics_desc=naics_value, user_email=get_user_res[0][0]['email_address'])
    if len(cc_update_values) > 0 or naics_value != '':
        logger.debug(f"create_user_constant_contact found values to update")
        cd = json.loads(output)
        cc.create_contact(cd)
    else:
        logger.debug(f"create_user_constant_contact nothing found to update")

def bk_watch_list_report(**kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_bk_query_watchlist_report')
    output = template.render(kwargs=kwargs)

    results = run_sql_queries_no_cache(output)
    logger.info(f"BK Watchlist Report: {results}")
    return results

def comp_watch_list_report(**kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_comp_query_watchlist_report')
    output = template.render(kwargs=kwargs)

    results = run_sql_queries_no_cache(output)
    logger.info(f"Comp Watchlist Report: {results}")
    return results

def update_user_industry(guid, **kwargs):
    update_user_industry = []
    industries_selected = kwargs['update_industries'].split(',')
    for i in industries_selected:
        update_user_industry.append({'key':guid, 'val': i})
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_user_update_industry')
    output = template.render(user_id=guid, update_user_industry=update_user_industry)

    del_user_industry(guid)
    return(run_sql_commit(output))

def del_user_industry(guid):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_user_del_industry')
    output = template.render(user_id=guid)

    return(run_sql_commit(output))

def view_pdf_form(**kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_bk_query_pdf')
    output = template.render(kwargs=kwargs)

    pdf_object_name = run_sql_queries_no_cache(output)
    return(gen_presigned_url('bpwa.pdf-storage', pdf_object_name[0][0]['pdf_filename']))

def view_pacer_docket(**kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_bk_query_docket_ft')
    output = template.render(kwargs=kwargs)
    results_ft = run_sql_queries_no_cache(output)
    docket_entry_w_file_type = results_ft[0]

    template = env.get_template('mysql_bk_query_docket_dt')
    output = template.render(kwargs=kwargs)
    results_dt = run_sql_queries_no_cache(output)
    docket_entry_w_full_listing = results_dt[0]
    
    ft_ids = []
    for ft in docket_entry_w_file_type:
        ft_ids.append(ft['id'])

    for r in docket_entry_w_full_listing:
        if r['id'] in ft_ids:
            found_entry = (next(item for item in docket_entry_w_file_type if item["id"] == r['id']))
            if found_entry:
                r['file_type'] = found_entry['file_type']
        else:
            r['file_type'] = 'other'
    return docket_entry_w_full_listing

def view_bankruptcies(guid, **kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template1 = env.get_template('mysql_view_bk')
    output1 = template1.render(bk_uid=guid, kwargs=kwargs)

    template2 = env.get_template('mysql_view_bk_loss_sum')
    output2 = template2.render(kwargs=kwargs)

    sql_query_results = run_sql_queries_no_cache(output1)
    sql_query_results_2 = run_sql_queries_no_cache(output2)

    try:
        if sql_query_results_2[0][0]['total_loss'] == None:
            sql_query_results[0][0]['total_loss'] = 0
        else:
            sql_query_results[0][0]['total_loss'] = int(sql_query_results_2[0][0]['total_loss'])
    except Exception as e:
        page_info = {
            'records': [], # all the response items will go in this array
            'count': 0, # current page
        }
        return(page_info, 200)
    else:
        return(sql_query_results)

def case_refresh(guid, **kwargs):
    logger.info(f"Case Refresh Triggered: {kwargs['dci_id'][0]}")
    # Init sub functions:
    db1 = dbSelectItems()
    db1.db_login()
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    user_info_results = get_user_information(guid)
    #logger.debug(user_info_results[0])
    # Check bk_pending_refreshes for dc_id
    pacer_data_results = None
    bk_refresh_exists = check_pending_bk_refresh(kwargs['dci_id'][0])
    current_refresh_count = user_info_results[0][0]['case_refresh_count']
    # Case Refresh Logic
    try:
        template = env.get_template('mysql_bk_case_data')
        output = template.render(kwargs=kwargs)
        sql_query_case_results = run_sql_queries_no_cache(output)
        logger.debug(f"case_refresh sql_query_case_results: {sql_query_case_results}")
        if user_info_results[0][0]['case_refresh_count'] < user_info_results[0][0]['case_refresh_max']:
            user_info_results[0][0]['case_refresh_count'] += 1
            uu_res = update_user(guid, case_refresh_count=user_info_results[0][0]['case_refresh_count'])
            logger.debug(f"case_refresh user_update_response: {uu_res}")
            # if exist - update table
            if bk_refresh_exists:
                logger.info(f"Case Refresh already in progress for: {kwargs['dci_id'][0]}")
                udpate_pending_bk_refresh(db1, guid, kwargs['dci_id'][0], 'insert')
                logger.debug(f"appending to case refresh: {guid}")
            else:
                # else add user_id to table for notification and run case refresh
                logger.debug(f"Pacer Session Triggered: {guid}")
                p1,p2 = pacer_login_session()
                udpate_pending_bk_refresh(db1, guid, kwargs['dci_id'][0], 'insert')
                pacer_data_results = build_pacer_data_from_sql(sql_query_case_results[0])
                parsed_pacer_results = parse_pacer_results(p1, p2, pacer_data_results, case_refresh_trigger=True)
                check_missing_204_data(parsed_pacer_results, case_refresh=kwargs['dci_id'][0])
        else:
            logger.debug(f"User: {guid} has reached refresh limit: {user_info_results[0][0]['case_refresh_count']}")
            return(f"User has reached refresh limit: {user_info_results[0][0]['case_refresh_count']}")
    except Exception as e:
        logger.error(f"API Funcs: Case Refresh Failed: {e}")
        db1.db_cnxn.rollback()
        cn = CaseNotify()
        suuid = shortuuid.uuid()
        cn.insert_user_notifications(uid=guid, title=f"Case Refresh Update", body=f"Failed to refreshed case: {sql_query_case_results[0][0]['case_name']}", type='refresh_failed', bkid=kwargs['dci_id'][0], actid=suuid)
        update_user(guid, case_refresh_count=current_refresh_count)
        bk_refresh_exists = check_pending_bk_refresh(kwargs['dci_id'][0])
        for b in bk_refresh_exists: #uid, title, body, type, bkid, actid=None
            #remove refresh data from table after run
            udpate_pending_bk_refresh(db1, b['user_id'], kwargs['dci_id'][0], 'delete')
        return '200'
    
    else:
        logger.info(f"Case Refresh Cleanup and Notificaiton Triggered")
        #send notifications to users in bk_pending_refresh - case refresh completed
        bk_refresh_exists = check_pending_bk_refresh(kwargs['dci_id'][0])

        cn = CaseNotify()
        for b in bk_refresh_exists: #uid, title, body, type, bkid, actid=None
            #remove refresh data from table after run
            udpate_pending_bk_refresh(db1, b['user_id'], kwargs['dci_id'][0], 'delete')
            
            suuid = shortuuid.uuid()
            cn.insert_user_notifications(uid=b['user_id'], title=f"Case Refresh Update", body=f"Successfully refreshed case: {sql_query_case_results[0][0]['case_name']}", type='refresh_ok', bkid=b['case_id'], actid=suuid)

    return '200'

def check_pending_bk_refresh(case_id):
    logger.debug(f"check_pending_bk_refresh triggered")
    db1 = dbSelectItems()
    db1.db_login()

    sql_query = f"SELECT * FROM `bk_pending_refreshes` WHERE case_id = {case_id}"
    sqlq_res = db1.fetch_no_cache(sql_query)
    return sqlq_res

def udpate_pending_bk_refresh(db1, guid, case_id, status):
    logger.debug(f"check_pending_bk_refresh triggered: {status}")
    #RUN delete on completion
    if status == 'insert':
        sql = f"INSERT INTO bk_pending_refreshes (`case_id`, `user_id`) VALUES ('{case_id}', '{guid}')"
    elif status == 'delete':
        sql = f"DELETE FROM bk_pending_refreshes WHERE case_id = '{case_id}' AND user_id = '{guid}'"
    else:
        logger.error(f"Update BK Refresh: status unknown")

    db1.sql_transaction(sql)
    db1.db_cnxn.commit()

def file_link_get(guid, call_pacer=True, **kwargs):
    logger.info(f"File Link Get Triggered: {kwargs}")
    #check table - docket_entry_file_links
    db1 = dbSelectItems()
    db1.db_login()
    connection = db_login()

    sql_query = f"SELECT id as docket_link_id ,docket_entry_name as filename, docket_entry_link as link FROM docket_entry_file_links WHERE \
         docket_entry_id = {kwargs['docket_entry_id'][0]}"
    sql_q_res = db1.fetch_no_cache(sql_query)
    if sql_q_res:
        logger.debug(f'file_link_get sql_q_res exists: {sql_q_res}')
        response = sql_q_res
        return response
    else:
        p1,p2 = pacer_login_session()        
        logger.debug(f'file_link_get get links from PACER')
        if call_pacer == True:
            logger.debug(f'file_link_get call_pacer == True')
            response = p1.get_html_file_links(kwargs['doc_url'][0])
            logger.debug(f'file_link_get response: {response}')
            for r in response:
                insert_docket_entry_file(connection, kwargs['docket_entry_id'][0], r['filename'], r['link'], kwargs['dci_id'][0])
            connection.close()
        else:
            logger.debug(f'file_link_get call_pacer == False')
            insert_docket_entry_file(connection, kwargs['docket_entry_id'][0], kwargs['filename'], kwargs['link'][0], kwargs['dci_id'][0])
            connection.close()
            return

    db1.db_login()
    connection = db_login()
    sql_query = f"SELECT id as docket_link_id ,docket_entry_name as filename, docket_entry_link as link FROM docket_entry_file_links WHERE \
    docket_entry_id = {kwargs['docket_entry_id'][0]}"    
    response = db1.fetch_no_cache(sql_query)    
    return response

def file_link_download(guid, **kwargs):
    logger.info(f"File Link Download Triggered")
    db1 = dbSelectItems()
    db1.db_login()
    connection = db_login()
    pdf_doc_files = []
    response = None
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    user_info_results = get_user_information(guid)
    logger.debug(user_info_results[0])
    logger.debug(f"downloading files: {user_info_results[0][0]['file_download_count']}, {user_info_results[0][0]['file_download_max']}")
    # Check if file download credits available 
    current_download_count = user_info_results[0][0]['file_download_count']
    logger.info(f"Checking User File Download Count")
    if user_info_results[0][0]['file_download_count'] < user_info_results[0][0]['file_download_max']:
        try:
            user_info_results[0][0]['file_download_count'] += 1
            # Increment file_download_count
            check_user_has_file_already = get_user_file_access(guid, dci_id=[kwargs['dci_id'][0]])
            if check_user_has_file_already:
                for c in check_user_has_file_already:
                    if c['docket_entry_link'] == kwargs['doc_url'][0]:
                        logger.debug(f"User already has access to file: {c['name']}")
                        return(gen_presigned_url('bpwa.pdf-storage', c['name']))
            else:
                logger.debug(f"User does NOT have access to file: {kwargs['doc_url'][0]}")
            update_user(guid, file_download_count=user_info_results[0][0]['file_download_count'])
            # Build case data object from kwargs
            logger.debug(f"User Download Count: {user_info_results[0][0]['file_download_count']}")
            template = env.get_template('mysql_bk_case_data')
            output = template.render(kwargs=kwargs)
            sql_query_case_results = run_sql_queries_no_cache(output)
            # Build pacer_data_results object from results
            pacer_data_results = build_pacer_data_from_sql(sql_query_case_results[0])
            # Format variables and build file name from case bits
            split_case_link = sql_query_case_results[0][0]['case_link'].split('?')
            split_case_number = sql_query_case_results[0][0]['case_number'].split(':')
            split_doc_url = kwargs['doc_url'][0].split('doc1/')
            file_name = f"{sql_query_case_results[0][0]['court_id']}.{split_case_link[1]}.{split_case_number[1]}.{split_doc_url[1]}.pdf"
            # Check against S3 objects before attempting download from PACER
            cas3_response = check_against_s3_objects(file_name)
            if cas3_response == True:
                logger.debug('File exists in S3, skipping purchase download')
                docket_link_id = doc_entry_file_link_table_id(connection, file_link=kwargs['doc_url'][0], case_id=kwargs['dci_id'][0])
                if docket_link_id:
                    logger.debug('file_link_download: docket_link_id exists!')
                ## add to docket_entry_file_links
                # set docket_link_id
                    response = 'Success'
                else:
                    logger.debug('file_link_download: docket_link_id NOT found!')
                    dtg_results = doc_table_get_id(connection, file_link=kwargs['doc_url'][0], case_id=kwargs['dci_id'][0])
                    logger.debug(f"file_link_download: dtg_results: {dtg_results}")
                    file_link_get(guid, dci_id=[kwargs['dci_id'][0]], filename=dtg_results[0][1], link=[kwargs['doc_url'][0]], docket_entry_id=[dtg_results[0][0]], call_pacer=False)
                    docket_link_id = doc_entry_file_link_table_id(connection, file_link=kwargs['doc_url'][0], case_id=kwargs['dci_id'][0])
                    logger.debug(f"file_link_download: dtg_results: {docket_link_id}")
                    response = 'Success'               
            else:
                logger.debug('File NOT found in S3, executing purchase flow')
                p1,p2 = pacer_login_session()
                file_name_w_path = f"results/{file_name}"
                # GET docket_table_id
                doc_ent_file_link_t_res = doc_entry_file_link_table_id(connection, file_link=kwargs['doc_url'][0], case_id=kwargs['dci_id'][0])
                logger.debug(f'file_link_download: doc_ent_file_link_t_res: {doc_ent_file_link_t_res}')
                if doc_ent_file_link_t_res:
                    docket_link_id = doc_ent_file_link_t_res
                else:                    
                    dtg_results = doc_table_get_id(connection, file_link=kwargs['doc_url'][0], case_id=kwargs['dci_id'][0])
                    #guid, **kwargs, call_pacer=True / kwargs['docket_entry_id'][0], r['filename'], r['link'], kwargs['dci_id'][0]
                    file_link_get(guid, dci_id=[kwargs['dci_id'][0]], filename=dtg_results[0][1], link=[kwargs['doc_url'][0]], docket_entry_id=[dtg_results[0][0]], call_pacer=False)
                    docket_link_id = doc_entry_file_link_table_id(connection, file_link=kwargs['doc_url'][0], case_id=kwargs['dci_id'][0])
                response = p2.download_pdf_files(kwargs['doc_url'][0], file_name_w_path, split_doc_url[0])
                # Upload file to S3 bucket
                upload_file(file_name_w_path, 'bpwa.pdf-storage', object_name=file_name)
            # Update DB - bkw_files table
            if response.find('Success') != -1:
                logger.debug('BK File response is Success')
                for p in pacer_data_results:
                    pdf_doc_files.append({'filename': file_name, 'link': kwargs['doc_url'][0], 'type': 'other'})
                    pacer_data_results[p]['pdf_doc_files'] = pdf_doc_files
                    pacer_data_results[p]['docket_files_link_id'] = docket_link_id
                    pacer_data_results[p]['dci_id'] = kwargs['dci_id'][0]
                insert_files_inventory(pacer_data_results)
                # Update DB - purchases table
                insert_purchases(connection, guid, pacer_data_results)
                return(gen_presigned_url('bpwa.pdf-storage', file_name))
            else:
                logger.error(f'BK File Download Failed - response is {response}')
                return 'File Download Failed'
        except Exception as e:
            logger.error(f'File Download Failed: {e}')
            update_user(guid, file_download_count=current_download_count)
            return 'File Download Failed'
    else:
        logger.warning(f"User: {guid} has reached download limit: {user_info_results[0][0]['file_download_count']}")
        return(f"User has reached download limit: {user_info_results[0][0]['file_download_count']}")

def build_pacer_data_from_sql(mysql_data_sets):
    logger.debug(f"build_pacer_data_from_sql triggered")
    pacer_data_results = {}
    for m in mysql_data_sets:
        pacer_data_results[m['case_name']] = {}
        pacer_data_results[m['case_name']]['case_number'] = m['case_number']
        pacer_data_results[m['case_name']]['court_id'] = m['court_id']
        pacer_data_results[m['case_name']]['date_filed'] = m['date_filed']
        pacer_data_results[m['case_name']]['cs_number'] = m['cs_number']
        pacer_data_results[m['case_name']]['cs_office'] = m['cs_office']
        pacer_data_results[m['case_name']]['cs_chapter'] = m['cs_chapter']
        pacer_data_results[m['case_name']]['case_link'] = m['case_link']
        pacer_data_results[m['case_name']]['pdf_dl_status'] = None
        pacer_data_results[m['case_name']]['bkw_filing_id'] = m['id']
    return pacer_data_results    

def check_missing_204_data(pacer_data_results, case_refresh=None):
    logger.info('Check Missing 204 Data Triggered')

    db1 = dbSelectItems()
    db1.db_login()
    connection = db_login()
    notify_204 = {}
    cn = CaseNotify()
    dc_id_list_for_not = []
    user_ids_for_notify = []
    notify_204_email_list = []
    loss_mysql_results = {}
    bkw_dt = BkwDateTime()
    sql_query = f"SELECT DISTINCT did FROM bankruptcies_watchlist"
    distinct_watchlist_dcid = db1.fetch_no_cache(sql_query)
    ###Get LOSS data info notification email###
    loss_file_loader = FileSystemLoader('templates/sql')
    loss_env = Environment(loader=loss_file_loader)
    loss_template = loss_env.get_template('mysql_loss_query_notification')
    for k in pacer_data_results:
        notify_204[pacer_data_results[k]['dci_id']] = {}
        if pacer_data_results[k]['parse_204206_attempt'] == True:
            loss_output = loss_template.render(dci_id=pacer_data_results[k]['dci_id'])
            loss_mysql_results = run_sql_queries_no_cache(loss_output)                
            update_data_bfd(connection, pacer_data_results)
            lst = [d['did'] for d in distinct_watchlist_dcid]
            if pacer_data_results[k]['dci_id'] in lst:
                sql_query = f"SELECT users.id as user_id,email_alerts_enabled,email_address,email_alert_1,email_alert_2,email_alert_3,users.date_added,subscription_status FROM users \
                LEFT JOIN bankruptcies_watchlist ON bankruptcies_watchlist.user_id = users.id \
                LEFT JOIN bankruptcy_filing_data ON bankruptcy_filing_data.dci_id = bankruptcies_watchlist.did \
                WHERE did = '{pacer_data_results[k]['dci_id']}'"
                user_data = db1.fetch_no_cache(sql_query)
                if user_data != None:
                    for u in user_data:                        
                        date_object = bkw_dt.get_thirty_day_time(u['date_added'])
                        date_object_split = str(date_object[0]).split(" ")
                        user_date_split = str(u['date_added']).split(" ")
                        user_date_added = datetime.strptime(user_date_split[0], "%Y-%m-%d") #Fix date for compare
                        thirty_days_from_date_added = datetime.strptime(str(date_object_split[0]), "%Y-%m-%d") #Fix date for compare
                        delta = thirty_days_from_date_added - user_date_added
                        if delta.days <= 14 or u['subscription_status'] == 'active':
                            if u['email_alerts_enabled'] == True:
                                notify_204_email_list.append(u['email_address'])
                                if u['email_alert_1']:
                                    notify_204_email_list.append(u['email_alert_1'])
                                if u['email_alert_2']:
                                    notify_204_email_list.append(u['email_alert_2'])
                                if u['email_alert_3']:
                                    notify_204_email_list.append(u['email_alert_3'])
                            user_ids_for_notify.append(u['user_id'])
                        else:
                            logger.warning(f"User does not meet notification criteria(active subscription)")
                        no_dupe_list = list(set(notify_204_email_list))
                        dc_id_list_for_not.append(pacer_data_results[k]['dci_id'])
                        notify_204[pacer_data_results[k]['dci_id']]['elist'] = no_dupe_list
                        notify_204[pacer_data_results[k]['dci_id']]['uids'] = user_ids_for_notify
                        notify_204[pacer_data_results[k]['dci_id']]['case_name'] = pacer_data_results[k]['case_name']
                else:
                    pass
    pacer_data_results.clear()
    if notify_204 and loss_mysql_results:
        logger.debug(f"Notifying users of 204 updates")
        cn.notify_bk_topic_creditors(dc_id_list_for_not, notify_204, loss_mysql_results[0])
    else:
        logger.debug(f"No loss results to notify")
        pass
    if case_refresh == None:
        cn.build_bk_topic()
    else:
        cn.build_bk_topic(case_refresh=case_refresh)

def case_existing_check(pacer_data_results, case_refresh_trigger=False):
    remove_list = []
    db1 = dbSelectItems()
    db1.db_login()
    
    for key in pacer_data_results:
        comp_scrub = company_scrub(key)
        comp_name = title(comp_scrub)
        pacer_data_results[key]['skip_201_parse'] = False
        pacer_data_results[key]['skip_204_parse'] = False
        sql_query = """SELECT * FROM bankruptcy_filing_data WHERE case_name = %s"""
        sqlq_results = db1.fetch_execute_v2(sql_query, comp_name)
        logger.debug(f"case_existing_check: {sqlq_results}")
        if sqlq_results:
            if sqlq_results[0]['status_201'] == True:
                pacer_data_results[key]['skip_201_parse'] = True
                logger.debug(f"Skipping 201: {key}")
            if sqlq_results[0]['status_204206'] == True:
                pacer_data_results[key]['skip_204_parse'] = True
                logger.debug(f"Skipping 204: {key}")
            if sqlq_results[0]['status_201'] == True and sqlq_results[0]['status_204206'] == True and case_refresh_trigger == False:
                remove_list.append(key)
                logger.debug(f"Removing the following already parsed cases: {key}")
    for r in remove_list:
        del pacer_data_results[r]
    return pacer_data_results

def parse_pacer_results(p1, p2, pacer_data_results, case_refresh_trigger=False):
    ## CLEAN UP ANY Stale PNG files
    logger.debug(f"parse_pacer_results triggered: refresh_trigger={case_refresh_trigger}")
    dir = 'results/pdf2png'
    filelist = glob.glob(os.path.join(dir, "*.png"))
    for f in filelist:
        os.remove(f)

    case_count = 0
    remove_list = []
    data_201_results = {}
    pacer_pdf_results = {}
    data_204206_results = {}
    data_204206_list_keys = []

    #Validate Cases as to not parse dupes
    pacer_data_results = case_existing_check(pacer_data_results, case_refresh_trigger=case_refresh_trigger)

    html_soup = None
    session_drm  = None
    html_tables_results = None
    pacer_data_results_204_key_list = ['court_id', 'cs_year', 'cs_number', 'cs_office', 'cs_chapter', 'date_filed', 'case_number', 'case_link',\
        'pdf_dl_status_201', 'pdf_dl_status_204206', 'pdf_dl_skip', 'company_city', 'company_state', 'company_zip', 'company_industry', 'company_address',\
        'pdf_filename', 'case_name']
    for k in pacer_data_results:
        session_drm = p1.pacer_dkt_rpt(pacer_data_results[k]['case_link'])
        if session_drm != None and session_drm != False:
            html_soup, pacer_user_session  = p1.pacer_post_for_html(pacer_data_results[k]['case_link'], pacer_data_results[k]['case_number'], pacer_data_results[k]['date_filed'])
        else:
            pass

        if html_soup != None and html_soup != False:
            html_tables_results = p2.parse_html_table_to_dic(k, html_soup)
        elif html_soup == 0:
            html_soup, pacer_user_session = p1.pacer_post_for_html(pacer_data_results[k]['case_link'], pacer_data_results[k]['case_number'], pacer_data_results[k]['date_filed'])
            html_tables_results = p2.parse_html_table_to_dic(k, html_soup)
        else:
            pass
        if html_tables_results != None and html_tables_results != False:
            try:
                p2.docket_table_parse(html_tables_results[k]['docket_table'], pacer_data_results, k)
                #pacer_data_results[k]['docket_table'] = object_name
            except Exception as e:
                logger.error(f"docket_table_parse failed: {e} -- {k}")        
        else:
            pass

    if html_tables_results != None and html_tables_results != False:
        try:
            p2.parse_docket_entries(html_tables_results, pacer_data_results, pacer_pdf_results)
        except Exception as e:
            logger.error(f"parse_docket_entries failed: {e} -- {k} -- {pacer_data_results}")
    else:
        pass        
    
    for k in pacer_data_results:
        case_count += 1
        logger.info(f"Working Case: {case_count} of {len(pacer_data_results.keys())}")
        #pacer_data_results[k]['docket_table'] = None
        data_201_results[k] = {}
        pacer_data_results[k]['case_name'] = k
        data_201_results[k]['naics_code'] = None
        data_201_results[k]['ein_number'] = None
        data_201_results[k]['estimated_assets_min'] = None
        data_201_results[k]['estimated_creditors_min'] = None
        data_201_results[k]['estimated_liabilities_min'] = None
        data_201_results[k]['estimated_assets_max'] = None
        data_201_results[k]['estimated_creditors_max'] = None
        data_201_results[k]['estimated_liabilities_max'] = None
        pacer_data_results[k]['parse_201_attempt'] = False
        pacer_data_results[k]['parse_204206_attempt'] = False
        pacer_data_results[k]['involuntary'] = False

        try:
            ein_string = str(html_tables_results[k]['tax_id_ein'])
            data_201_results[k]['ein_number'] = ein_string.replace('-', '')
        except:
            data_201_results[k]['ein_number'] = None

        if 'skip_201_parse' in pacer_data_results[k] and 'skip_204_parse' in pacer_data_results[k]:
            if pacer_data_results[k]['skip_201_parse'] == True and pacer_data_results[k]['skip_204_parse'] == True:
                logger.info(f"Skipping 201/204 parse: {k}")
                pass
            else:
                try:
                    if pacer_data_results[k]['pdf_dl_status_201'] == 'complete' or pacer_data_results[k]['pdf_dl_status_204206'] == 'complete':
                        logger.info(f"Running 201 / 204 parser: {k}")
                        for pdf_results_key in pacer_pdf_results[k]:
                            png_list = convert_pdf2png(pdf_results_key, 'bpwa.parse-png', pacer_pdf_results[k][pdf_results_key])

                            for p in png_list:
                                documentName = p
                                s3BucketName = 'bpwa.parse-png'                        
                                pdf_png_meta_data = rawtext_pdffromimage(p, s3BucketName)
                                if pacer_data_results[k]['skip_201_parse'] == True:
                                    logger.info(f"Skipping 201/205 parse: {k}")
                                    pass
                                else:
                                    if 'page 2'in pdf_png_meta_data and 'official form 201' in pdf_png_meta_data:
                                        naics_code_results = get_naics_code(pdf_png_meta_data, p)

                                        try:
                                            if naics_code_results != None:
                                                data_201_results[k]['naics_code'] = naics_code_results
                                            else:
                                                pass
                                        except Exception as e:
                                            pass
                                    if 'page 3' in pdf_png_meta_data and 'official form 201' in pdf_png_meta_data:
                                        pacer_data_results[k]['parse_201_attempt'] = True
                                        data_201_results = parse_201(s3BucketName, documentName, data_201_results, k, pg='3')
                                    if 'page 4' in pdf_png_meta_data and 'official form 201' in pdf_png_meta_data:
                                        pacer_data_results[k]['parse_201_attempt'] = True
                                        data_201_results.update(parse_201(s3BucketName, documentName, data_201_results, k, pg='4'))
                                    if 'official form 205' in pdf_png_meta_data:
                                        data_201_results = parse_205(pacer_data_results=pacer_data_results)
                                if pacer_data_results[k]['skip_204_parse'] == True:
                                    pass
                                else:
                                    if 'official form 204' in pdf_png_meta_data:
                                        pacer_data_results[k]['parse_204206_attempt'] = True
                                        data_204206_results = parse_204(s3BucketName, documentName, pacer_data_results, k, data_201_results[k]['naics_code'])
                                    if 'top unsecured creditors' in pdf_png_meta_data:
                                        pacer_data_results[k]['parse_204206_attempt'] = True
                                        data_204206_results = parse_204(s3BucketName, documentName, pacer_data_results, k, data_201_results[k]['naics_code'])
                                    if 'amount of unsecured claim' in pdf_png_meta_data:
                                        pacer_data_results[k]['parse_204206_attempt'] = True
                                        data_204206_results = parse_204(s3BucketName, documentName, pacer_data_results, k, data_201_results[k]['naics_code'])
                                    if 'priority creditor\'s name and mailing address' in pdf_png_meta_data:
                                        pacer_data_results[k]['parse_204206_attempt'] = True
                                        data_204206_results = parse_206(pdf_png_meta_data, documentName, pacer_data_results, k, data_201_results[k]['naics_code'])
                                    if 'nonpriority creditor\'s name and mailing address' in pdf_png_meta_data:
                                        pacer_data_results[k]['parse_204206_attempt'] = True
                                        data_204206_results = parse_206(pdf_png_meta_data, documentName, pacer_data_results, k, data_201_results[k]['naics_code'])
                                    else:
                                        pass
                                ## CLEAN UP
                                try:
                                    cleanup_png_file = 'results/pdf2png/' + p
                                    os.remove(cleanup_png_file)
                                except Exception as e:
                                    logger.error(f"file cleanup error: {e}")
                    else:
                        remove_list.append(k)
                        logger.warning(f"check PDF status: {e}, {k}")
                except Exception as e:
                    remove_list.append(k)
                    logger.error(f"check PDF status: {e}, {k}")

    # Remove if in list from results
    for r in remove_list:
        if r in data_201_results:
            del data_201_results[r]
        elif r in data_204206_results:
            del data_204206_results[r]
        else:
            pass
    # Remove 204 data if no case data found
    for key in data_204206_results:
        for dk in data_204206_results[key]:
            if dk in pacer_data_results_204_key_list:
                pass
            else:
                data_204206_list_keys.append(dk.strip())

    connection = db_login()
    pacer_data_remove = []
    logger.info(f"WERE HERE, check data: {data_201_results}")
    if not connection is None:
        for k in pacer_data_results:
            if k == " ":
                pass
            else:
                try: # Insert companies first - ALWAYS
                    insert_companies(connection, k, data_201_results[k]['naics_code'])
                except Exception as e:
                    logger.warning(f"Failed to insert company: {k}, Error: {e}")
                    pacer_data_remove.append(k)
        for p in pacer_data_remove:
            del pacer_data_results[p]
        # Next build data around inserted company
        insert_company_ein(connection, data_201_results, pacer_data_results)
        insert_data_dci(connection, pacer_data_results)
        insert_data_bfd(connection, pacer_data_results)
        insert_docket_data(connection, pacer_data_results)
        #if case_refresh_trigger == False:
        insert_docket_entry_file(connection, pdr=pacer_data_results)
        insert_data_b201d(connection, data_201_results, pacer_data_results)
        insert_files_inventory(pacer_data_results)
        # Fix up and Insert Unsecured Data
        for k in data_204206_results:
            for kv in data_204206_results[k]:
                if kv.strip() in data_204206_list_keys:
                    try:
                        comp_name_fixed = re.split('(?i)attn:|attn|c\/o|esq\.|esq|esquire',data_204206_results[k][kv]['creditor_company_name'])
                        if len(comp_name_fixed) > 0:
                            logger.debug(f"data_204206 comp_name_fixed: found")
                            insert_companies(connection, comp_name_fixed[0].strip(), data_204206_results[k][kv]['industry'])
                            insert_data_b204206d(connection, comp_name_fixed[0].strip(), data_204206_results[k][kv]['creditor_company_zip'], data_204206_results[k][kv]['nature_of_claim'].upper(), data_204206_results[k][kv]['unsecured_claim_value'], data_204206_results[k][kv]['industry'], pacer_data_results[k]['bkw_filing_id'])
                        else:
                            insert_companies(connection, data_204206_results[k][kv]['creditor_company_name'].strip(), data_204206_results[k][kv]['industry'])
                            insert_data_b204206d(connection, data_204206_results[k][kv]['creditor_company_name'].strip(), data_204206_results[k][kv]['creditor_company_zip'], data_204206_results[k][kv]['nature_of_claim'].upper(), data_204206_results[k][kv]['unsecured_claim_value'], data_204206_results[k][kv]['industry'], pacer_data_results[k]['bkw_filing_id'])
                    except Exception as e:
                        logger.warning(f"data_204206 exception: {e} -- {kv}")
                    # Parse Phone/Email from Creditors
                    joined_string_phone = None
                    joined_string_email = None
                    try:
                        comp_name_fixed = re.split('(?i)attn:|attn|c\/o|esq\.|esq|esquire',data_204206_results[k][kv]['creditor_company_name'])
                        if len(data_204206_results[k][kv]['creditor_email']) > 0:
                            joined_string_phone = ",".join(data_204206_results[k][kv]['creditor_phone'])
                        if len(data_204206_results[k][kv]['creditor_phone']) > 0:
                            joined_string_email = ",".join(data_204206_results[k][kv]['creditor_email'])
                            if len(comp_name_fixed) > 0:
                                insert_data_additional_info(connection, comp_name_fixed[0].strip(), joined_string_email, joined_string_phone, pacer_data_results[k]['bkw_filing_id'])
                            else:
                                insert_data_additional_info(connection,  data_204206_results[k][kv]['creditor_company_name'].strip(), joined_string_email, joined_string_phone, pacer_data_results[k]['bkw_filing_id'])
                        else:
                            pass
                    except Exception as e:
                        pass
                else:
                    pass
    else:
        logger.error("DB Login Failed!")
    ## THE END ######
    # HOUSE KEEPING #
    connection.close()

    dir = 'results/'
    filelist = glob.glob(os.path.join(dir, "*.pdf"))
    for f in filelist:
        os.remove(f)

    return pacer_data_results

def run_sql_queries(query, my_query_count):
    #logger.debug(f"{query}, {my_query_count}")
    db1 = dbSelectItems()
    db1.db_login()
    if db1.db_cnxn != None:
        my_query_result = db1.fetch(query)
        my_query_result_count = db1.fetch(my_query_count)
        page_info = {
              'records': my_query_result, # all the response items will go in this array
              'count': my_query_result_count[0]['result_count'], # current page
        }
        db1.db_cnxn.close()
        return(page_info, 200)
    else:
        db1.db_cnxn.close()
        return('SQL Query Failed', 500)
    
def run_sql_queries2(sql_query):
    #logger.debug(sql_query)
    db1 = dbSelectItems()
    db1.db_login()
    if db1.db_cnxn != None:
        my_query_result = db1.fetch(sql_query)
        db1.db_cnxn.close()
        return(my_query_result, 200)
    else:
        db1.db_cnxn.close()
        return('SQL Query Failed', 500)

def run_sql_queries_no_cache(query, my_query_count=None):
    #logger.debug(f"{query}")
    db1 = dbSelectItems()
    db1.db_login()
    if my_query_count == None:
        #logger.debug('run_sql_queries_no_cache: my_query_count is None')
        if db1.db_cnxn != None:
            my_query_result = db1.fetch_no_cache(query)
            return(my_query_result, 200)
        else:
            return('SQL Query Failed', 500)
    else:
        #logger.debug('run_sql_queries_no_cache: my_query_count is NOT None')
        if db1.db_cnxn != None:
            my_query_result = db1.fetch_no_cache(query)
            my_query_result_count = db1.fetch_no_cache(my_query_count)
            page_info = {
                  'records': my_query_result, # all the response items will go in this array
                  'count': my_query_result_count[0]['result_count'], # current page
            }
            return(page_info, 200)
        else:
            return('SQL Query Failed', 500)


def run_sql_queries_no_cache_v2(query, value):
    #logger.debug(f"{query}")
    db1 = dbSelectItems()
    db1.db_login()
    if db1.db_cnxn != None:
        my_query_result = db1.fetch_execute(query, value)
        db1.db_cnxn.close()
        return(my_query_result, 200)
    else:
        db1.db_cnxn.close()
        return('SQL Query Failed', 500)

def run_sql_commit(sql_query):
    db1 = dbSelectItems()
    db1.db_login()
    if db1.db_cnxn != None:
        my_query_result = db1.sql_commit(sql_query)
        return(my_query_result, 200)
    else:
        return('Query Failed', 500)
    #db1.flush_cache()

def run_sql_commit_many(sql_query, data):
    #logger.debug(sql_query)
    db1 = dbSelectItems()
    db1.db_login()
    if db1.db_cnxn != None:
        my_query_result = db1.sql_commit_many(sql_query, data)
        return(my_query_result, 200)
    else:
        return('Query Failed', 500)

def run_sql_truncate(table):
    logger.debug(table)
    db1 = dbSelectItems()
    db1.db_login()
    if db1.db_cnxn != None:
        my_query_result = db1.sql_truncate(table)
        return(my_query_result, 200)
    else:
        return('Query Failed', 500)        

def add_bk_watchlist(guid, **kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template_count = env.get_template('mysql_bk_watchlist_get_count')
    output_count = template_count.render(bk_uid=guid)

    template = env.get_template('mysql_bk_watchlist_add')
    output = template.render(kwargs=kwargs, user_id=guid)

    template2 = env.get_template('mysql_bk_id_name')
    output2 = template2.render(kwargs=kwargs)

    result_out_count = run_sql_queries_no_cache(output_count)
    logger.debug(f"BK-WL entry count: {result_out_count[0][0]['entries']}")
    if int(result_out_count[0][0]['entries']) <= 14:
        result = run_sql_commit(output)
        result2 = run_sql_queries_no_cache(output2)
        split_name = result2[0][0]['case_number'].split(':')
        tn = f"{result2[0][0]['slug']}-{split_name[1]}"
        if result[1] == 200:
            pass
        else:
            logger.error(f"BK watchlist add failed: {kwargs['id']}")
            return 500
    else:
        logger.warning(f"User watch list limit reached: {kwargs['id']}")
        return (result_out_count[0][0]['entries'], 500)
    return result

def del_bk_watchlist(guid, **kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template_bk_id_name = env.get_template('mysql_bk_id_name')
    output_bk_id_name = template_bk_id_name.render(kwargs=kwargs)
    result_bk_id_name = run_sql_queries_no_cache(output_bk_id_name)

    split_name = result_bk_id_name[0][0]['case_number'].split(':')
    tn = f"bkw-{result_bk_id_name[0][0]['slug']}-{split_name[1]}"

    template = env.get_template('mysql_bk_watchlist_del')
    output = template.render(kwargs=kwargs, user_id=guid)
    return(run_sql_commit(output))

def list_bankruptcies_watchlist(guid, **kwargs):
    """
    This function responds to a request for /pyapi/list_bankruptcies
    with the selected DB data results returned for all bankruptcies joined data

    :return:        Database Query Results Dictionary
    """
    logger.debug(f"list_bankruptcies_watchlist triggered")
    bk_filters = []
    bk_filters_asset = []
    bk_filters_chapter = []
    bk_filters_creditor = []
    bk_filters_liability = []
    bk_filters_industries = []
    kwargs['offset'] = (int(kwargs['page'][0]) - 1) * int(kwargs['page_size'][0])
    try:
        if kwargs['search'][0] == None:
            pass
        else:
            quote_val = kwargs['search'][0]
            bk_filters.append({'key': 'case_name', 'val': quote_val})
    except:
        pass

    try:
        if kwargs['industries'] == 0:
            pass
        else:
            for i in kwargs['industries']:
                bk_filters_industries.append({'key': 'industry_desc.id', 'val': i})
    except:
        pass
    try:
        if kwargs['chapter_types'] == 0:
            pass
        else:
            for i in kwargs['chapter_types']:
                bk_filters_chapter.append({'key': 'cs_chapter', 'val': i})
    except:
        pass

    try:
        if kwargs['creditor_ranges'] == 0:
            pass
        else:
            for i in kwargs['creditor_ranges']:
                bk_filters_creditor.append({'key': 'estimated_creditors.id', 'val': i})
    except:
        pass
    try:
        if kwargs['asset_ranges'] == 0:
            pass
        else:
            for i in kwargs['asset_ranges']:
                bk_filters_asset.append({'key': 'estimated_assets.id', 'val': i})
    except:
        pass

    try:
        if kwargs['liability_ranges'] == 0:
            pass
        else:
            for i in kwargs['liability_ranges']:
                bk_filters_liability.append({'key': 'estimated_liabilities.id', 'val': i})
    except:
        pass

    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_bk_watchlist_get')
    output = template.render(kwargs=kwargs, bk_filters=bk_filters, bk_filters_asset=bk_filters_asset, \
    bk_filters_chapter=bk_filters_chapter, bk_filters_creditor=bk_filters_creditor, \
    bk_filters_liability=bk_filters_liability, bk_filters_industries=bk_filters_industries, \
    bk_uid=guid)
    logger.debug(f"list_bankruptcies_watchlist: sql: {output}")
    query_drop_line = "\n".join(output.split("\n")[:-3])
    query_count = re.sub(r'(SELECT).*(FROM)', r'SELECT COUNT(*) as result_count FROM', query_drop_line, flags=re.DOTALL | re.M)
    list_watch_res = (run_sql_queries_no_cache(output, query_count))
    logger.debug(f"list-watch-res: {list_watch_res}")
    return list_watch_res

def add_comp_watchlist(guid, **kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template_count = env.get_template('mysql_comp_watchlist_get_count')
    output_count = template_count.render(bk_uid=guid)

    template = env.get_template('mysql_comp_watchlist_add')
    template2 = env.get_template('mysql_comp_id_name')
    output2 = template2.render(kwargs=kwargs, user_id=guid)
    result_out_count = run_sql_queries_no_cache(output_count)
    logger.debug(f"Comp-WL entry count: {result_out_count[0][0]['entries']}")
    if int(result_out_count[0][0]['entries']) <= 14:
        result2 = run_sql_queries_no_cache(output2)
        output = template.render(kwargs=kwargs, user_id=guid, comp_slug=result2[0][0]['slug'])
        result = run_sql_commit(output)
        tn = f"{result2[0][0]['slug']}-{result2[0][0]['id']}"
        if result[1] == 200:
            pass
        else:
            logger.error(f"Comp watchlist add failed: {kwargs['id']}")
            return 500
    else:
        logger.warning(f"User watch list limit reached: {kwargs['id']}")
        return (result_out_count[0][0]['entries'], 400)
    return result

def del_comp_watchlist(guid, **kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template_comp_id_name = env.get_template('mysql_comp_id_name')
    output_comp_id_name = template_comp_id_name.render(kwargs=kwargs)
    result_comp_id_name = run_sql_queries_no_cache(output_comp_id_name)

    tn = f"bkw-{result_comp_id_name[0][0]['slug']}-{result_comp_id_name[0][0]['id']}"

    template = env.get_template('mysql_comp_watchlist_del')
    output = template.render(kwargs=kwargs, user_id=guid)
    return(run_sql_commit(output))

def list_comp_watchlist(guid, **kwargs):
    """
    This function responds to a request for /pyapi/list_bankruptcies
    with the selected DB data results returned for all bankruptcies joined data

    :return:        Database Query Results Dictionary
    """
    naics_filters = []
    loss_filters_dc_id = []
    loss_filters_search = []
    loss_filters_unsecured_values = []
    template, query_count = None, None
    kwargs['offset'] = (int(kwargs['page'][0]) - 1) * int(kwargs['page_size'][0])

    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    max_r = False

    try:
        if kwargs['loss'][0] == 0 and kwargs['loss'][1] == 0:
            pass
        else:
            loss_filters_unsecured_values.append({'key': 'unsecured_claim_min', 'val': kwargs['loss'][0], 'sign': '>'})
            loss_filters_unsecured_values.append({'key': 'unsecured_claim_max', 'val': kwargs['loss'][1], 'sign': '<'})
    except Exception as e:
        pass

    try:
        if kwargs['search'][0] == None:
            pass
        else:
            quote_val = kwargs['search'][0]
            loss_filters_search.append({'key': 'creditor_name', 'val': quote_val})
    except:
        pass

    try:
        if len(kwargs['industries']) == 0:
            pass
        else:
            for i in kwargs['industries']:
                naics_filters.append({'key': 'companies.industry_id', 'val': i})
    except:
        pass

    try:
        if kwargs['id'][0] == None:
            pass
        else:
            quote_val = kwargs['id'][0]
            loss_filters_dc_id.append({'key': 'dc_id', 'val': quote_val})
    except:
        pass

    try:
        if kwargs['max_losses_per_case'][0] == None:
            pass
        else:
            max_r = True
            kwargs['umax_results'] = [kwargs['max_losses_per_case'][0]]
    except:
        pass

        template = env.get_template('mysql_comp_watchlist_get')
        output = template.render(kwargs=kwargs, loss_filters_search=loss_filters_search, naics_filters=naics_filters, \
        loss_filters_unsecured_values=loss_filters_unsecured_values, loss_filters_dc_id=loss_filters_dc_id, user_id=guid)
        query_drop_line = "\n".join(output.split("\n")[:-3])
        query_count = re.sub(r'(SELECT).*(FROM)', r'SELECT COUNT(*) as result_count FROM', query_drop_line, flags=re.DOTALL | re.M)

    return (run_sql_queries_no_cache(output, query_count))

def add_notification_subscription(tn, guid, id, type):
    """
    This function handles watch_list topic and subscription logic
    When a user adds a company/bankruptcy we query user alerts and configure
    the topic and subscription based on the users settings

    :params:        topic_name, guid

    :return:        None
    """
    t_names = {}
    resposne = None
    topic_name = tn
    tn = f"bkw-{topic_name}"
    sns = SNSTopic()
    list_topics_resp = sns.list_topics()

    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_user_subarn_add')

    file_loader_tarn = FileSystemLoader('templates/sql')
    env_tarn = Environment(loader=file_loader_tarn)
    tarn_template = env_tarn.get_template('mysql_user_toparn_add')

    if type == 'bk':
        table_name = 'user_notify_cases'
    elif type == 'comp':
        table_name = 'user_notify_companies'
    else:
        table_name = None

    logger.info(f"Attempting to subscribe: {tn}")
    try:
        if list_topics_resp['ResponseMetadata']['HTTPStatusCode'] == 200:
            for arn in list_topics_resp['Topics']:
                arn_name = arn['TopicArn'].split(':')
                t_names[arn['TopicArn']] = arn_name.pop()

            if topic_name in t_names.values():
                response = [key for key, value in t_names.items() if value == topic_name]
                logger.debug(f"Topic exists: {response}")
            else:
                response = sns.create_topic(tn)
        else:
            logger.error(f"List topics failed: {list_topics_resp['ResponseMetadata']}")
    except ClientError:
        logger.error(f"Creating topic failed: {tn}")
        pass
    else:
        logger.debug(f"Adding Subscription to topic: {tn}" )
    # GET CURRENT USER INFO (PHONE / EMAIL)
    email_alerts = ['email_alert_1', 'email_alert_2', 'email_alert_3']
    text_alerts = ['phone_alert_1', 'phone_alert_2', 'phone_alert_3']
    uio = get_user_information(guid)
    if uio[0][0]['text_alerts_enabled'] == True:
        for i in text_alerts:
            if uio[0][0][i]:
                try:
                    ts_resp = sns.topic_subscribe(topic_arn=response, protocol='sms', endpoint=uio[0][0][i])
                    tarn_output = tarn_template.render(topic_name=tn, topic_arn=response)
                    output = template.render(sub_arn=ts_resp, user_id=guid, topic_name_sub=tn, user_notify_table=table_name, \
                    aws_topic_arn=response, track_id=id)
                    run_sql_commit(tarn_output)
                    run_sql_commit(output)
                except Exception as e:
                    logger.error(f"Sub to topic SMS failed: {tn}: {e}")
                    pass
                else:
                    logger.debug(f"Subscription to SMS topic successs: {tn}")

    if uio[0][0]['email_alerts_enabled'] == True:
        for i in email_alerts:
            if uio[0][0][i]:
                try:
                    ts_resp = sns.topic_subscribe(topic_arn=response, protocol='email', endpoint=uio[0][0][i])
                    tarn_output = tarn_template.render(topic_name=tn, topic_arn=response)
                    output = template.render(sub_arn=ts_resp, user_id=guid, topic_name_sub=tn, user_notify_table=table_name, \
                    aws_topic_arn=response, track_id=id)
                    run_sql_commit(tarn_output)
                    run_sql_commit(output)
                except Exception as e:
                    logger.error(f"Sub to topic EMAIL failed: {tn}: {e}")
                    pass
                else:
                    logger.debug(f"Subscription to EMAIL topic successs: {tn}")

def del_notification_subscription(topic_name, guid, table_name):
    """
    This function handles SNS notification subscription removal
    and Topic removal if no subscriptions - this aids in keeping us from
    hitting the AWS 100,000 topic creation for one account.

    :params:        topic_name

    :return:        200
    """
    st1 = SNSTopic()
    subs_by_topic_resp = None
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_user_subarn_get')
    output = template.render(user_id=guid, topic_name_sub=topic_name, user_notify_table=table_name)

    # DELETE Topic query
    env_del = Environment(loader=file_loader)
    template_del = env_del.get_template('mysql_user_toparn_del')
    output_del = template_del.render(topic_name=topic_name)

    sql_resp = run_sql_queries_no_cache(output)
    logger.debug(sql_resp)
    for s in sql_resp[0]:
        logger.debug(f"UN-SUB-ARN: {s['aws_sub_arn']}")
        st1.unsub_to_topic(s['aws_sub_arn'])

    # remove from subscription db table
    del_template = env.get_template('mysql_user_subarn_del')
    del_output = del_template.render(user_id=guid, topic_name_sub=topic_name, user_notify_table=table_name)
    run_sql_commit(del_output)
    # check if any active subscriptions to topic arn
    list_topics_resp = st1.list_topics()
    if list_topics_resp['ResponseMetadata']['HTTPStatusCode'] == 200:
        for arn in list_topics_resp['Topics']:
            if re.search(topic_name, arn['TopicArn']):
                subs_by_topic_resp = st1.list_subs_by_topic(arn['TopicArn'])
                if subs_by_topic_resp['Subscriptions']:
                    pass
                else:
                    # Delete from AWS to reduce hitting limit of 200K
                    st1.delete_topic(arn['TopicArn'])
                    # remove from aws_topic_information table
                    run_sql_commit(output_del)
            else:
                pass

def get_user_information(guid):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_user_info_get')
    output = template.render(user_id=guid)

    user_info_object = run_sql_queries_no_cache(output)
    return(user_info_object)


def get_user_file_access(guid,**kwargs):
    logger.debug('get_user_file_access triggered')
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    ret_results = None

    if 'dci_id' in kwargs:
        logger.debug('dci_id flow executed')
        template = env.get_template('mysql_user_file_access_get')
        output = template.render(user_id=guid, case_id=kwargs['dci_id'][0])
    else:
        logger.debug('dci_id NOT found flow executed')
        template = env.get_template('mysql_user_file_access_get_all')
        output = template.render(user_id=guid)

    template = env.get_template('mysql_user_file_access_get_pet_creds')
    output2 = template.render(user_id=guid, case_id=kwargs['dci_id'][0])

    user_info_object = run_sql_queries_no_cache(output)
    logger.debug(f"UIO: {user_info_object}")

    user_info_object2 = run_sql_queries_no_cache(output2)
    logger.debug(f"UIO2: {user_info_object2}")

    ret_results = user_info_object2[0]
    if user_info_object:
        #ret_results = {**user_info_object[0][0], **user_info_object2[0][0]}
        ret_results = list({x['name']:x for x in user_info_object[0] + user_info_object2[0]}.values())
    logger.debug(f"ret_results: {ret_results}")
    return(ret_results)

def list_cities(**kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)

    template = env.get_template('mysql_cities_list')
    output = template.render(kwargs=kwargs)

    get_cities_result = run_sql_queries_no_cache(output)
    return(get_cities_result)

def list_notifications(guid, **kwargs):
    list_not_filters = []
    list_not_limit = None
    for key, value in kwargs.items():
        try:
            if value[0] == '':
                pass
            elif key == 'limit':
                list_not_limit = value[0]
            elif value[0] == 'all':
                pass
            elif value[0] == 'all':
                pass
            elif value[0] == 'true' or value[0] == 'false' or type(value[0]) == int:
                list_not_filters.append({'key': key, 'val': value[0]})
            else:
                value = '\'' + value[0] + '\''
                list_not_filters.append({'key': key, 'val': value})
        except:
            pass

    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_notifications_list')
    output = template.render(guid=guid, list_not_filters=list_not_filters, list_not_limit=list_not_limit)

    get_notifications_result = run_sql_queries_no_cache(output)
    return(get_notifications_result)

def read_notification(**kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_notification_read')
    output = template.render(kwargs=kwargs)
    notification_read = run_sql_commit(output)
    return(notification_read)

def delete_notification(**kwargs):
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_notification_delete')
    output = template.render(kwargs=kwargs)
    notification_del = run_sql_commit(output)
    return(notification_del)

def read_notifications(guid, **kwargs):
    notifications_mark_read = list_notifications(guid, **kwargs)
    for n in notifications_mark_read[0]:
        read_notification(id=n['id'])
    return('200')

def delete_notifications(guid, **kwargs):
    notifications_mark_read = list_notifications(guid, **kwargs)
    for n in notifications_mark_read[0]:
        delete_notification(id=n['id'])
    return('200')

def change_password(auth0_uid, **kwargs):
    rs = requests.Session()
    token = auth0_managment_api_key()
    payload = {"password": f"{kwargs['password']}", "connection": "Username-Password-Authentication"}
    auth0_password_url = f"https://{os.environ['AUTH0_DOMAIN']}/api/v2/users/{auth0_uid}"
    #login_headers = {'content-type': 'application/json', 'authorization': "Bearer " + os.environ['AUTH0_BEARER_TOKEN']}
    login_headers = {'content-type': 'application/json', 'authorization': "Bearer " + token}

    try:
       response = rs.patch(url=auth0_password_url, headers=login_headers, json=payload)
    except:
        return 'Change password failed'

    if response.status_code == 200:
        return 'Change password successful'
    else:
        logger.warning(response.text)
        return 'Change password failed'

def auth0_managment_api_key():
  # Configuration Values
  domain = os.environ['AUTH0_DOMAIN']
  audience = f'https://{domain}/api/v2/'
  client_id = os.environ['AUTH0_M2M_CLIENT_ID']
  client_secret = os.environ['AUTH0_M2M_CLIENT_SECRET']
  grant_type = "client_credentials" # OAuth 2.0 flow to use

  # Get an Access Token from Auth0
  base_url = f"https://{domain}"
  payload =  { 
    'grant_type': grant_type,
    'client_id': client_id,
    'client_secret': client_secret,
    'audience': audience
  }
  response = requests.post(f'{base_url}/oauth/token', data=payload)
  oauth = response.json()
  access_token = oauth.get('access_token')

  return access_token


def generate_bk_digest(schedule, title, sub_line):
    ###Get BK data info daily digest###
    cc_user_ids = []
    email_list = []

    bkw_dt = BkwDateTime()
    date_object = bkw_dt.get_daily_time_w_month_day()#get_timestamp_day_now_month_day

    if schedule == 'daily':
        dt,dp,dm,dd = get_daily_time()
        bk_env_get_template = 'mysql_bk_query_filter_digest'
        loss_env_get_template = 'mysql_loss_query_filter_digest'
    elif schedule == 'weekly':
        dt,dp = get_weekly_time()
        bk_env_get_template = 'mysql_bk_query_filter_digest_weekly'
        loss_env_get_template = 'mysql_loss_query_filter_digest_weekly'        
    elif schedule == 'bi_weekly':
        dt,dp = get_bi_weekly_time()
    # SQL Template / jinja2
    #dp = '2022-12-15'
    #dt = '2022-12-16'
    bk_file_loader = FileSystemLoader('templates/sql')
    bk_env = Environment(loader=bk_file_loader)
    bk_template = bk_env.get_template(bk_env_get_template)
    bk_output = bk_template.render(sdf=dp, edf=dt)
    bk_mysql_results = run_sql_queries_no_cache(bk_output)

    ###Get LOSS data info daily digest###
    loss_file_loader = FileSystemLoader('templates/sql')
    loss_env = Environment(loader=loss_file_loader)
    loss_template = loss_env.get_template(loss_env_get_template)
    loss_output = loss_template.render(sdf=dp, edf=dt)
    loss_mysql_results = run_sql_queries_no_cache(loss_output)

    ###BUILD HTML data from SQL results###
    file_loader_html = FileSystemLoader('templates/html')
    env_html = Environment(loader=file_loader_html)
    html_template_daily_bk_w_creditor = env_html.get_template('bkw_daily_digest_v2')
    date_formatted = bkw_dt.get_timestamp_day_now_month_day()
    html_output_creditor = html_template_daily_bk_w_creditor.render(loss_data=loss_mysql_results[0], bk_data=bk_mysql_results[0], date=date_formatted)
    
    cc = ConstantContact()

    if schedule == 'weekly':
        df_1 = pd.DataFrame(loss_mysql_results[0])
        df_2 = pd.DataFrame(bk_mysql_results[0])
        writer2 = pd.ExcelWriter('data.xlsx')
        df_1.to_excel(writer2, sheet_name='Impacted Businesses', index=False)
        df_2.to_excel(writer2, sheet_name='Corporate Bankruptcies', index=False)
        writer2.save()
        #Upload report to S3
        weekly_report_title = f'BKwire Weekly Digest - {date_object[2]} {date_object[3]}.xlsx'
        upload_file('data.xlsx', 'bkw.weekly.reports', object_name=weekly_report_title)
        #application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        gpu_response = gen_presigned_url('bkw.weekly.reports', weekly_report_title, responsectype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', expiry=86400)
        ###BUILD HTML data from SQL results###
        file_loader_html = FileSystemLoader('templates/html')
        env_html = Environment(loader=file_loader_html)
        html_template_daily_bk_w_creditor = env_html.get_template('bkw_weekly_digest_v2')
        html_output_creditor = html_template_daily_bk_w_creditor.render(presigned_url=gpu_response, week_of_date=f"{date_object[2]} {date_object[3]}")        

    daily_notification_sub = f"SELECT email_address, email_alert_1, email_alert_2, email_alert_3, subscription_status, date_added FROM users WHERE {schedule} = 1 AND email_alerts_enabled = 1"
    not_sub_results = run_sql_queries_no_cache(daily_notification_sub)

    for m in not_sub_results[0]:
        date_object2 = bkw_dt.get_thirty_day_time(m['date_added'])
        date_object_split = str(date_object2[0]).split(" ")
        user_date_split = str(m['date_added']).split(" ")
        user_date_added = datetime.strptime(user_date_split[0], "%Y-%m-%d") #Fix date for compare
        thirty_days_from_date_added = datetime.strptime(str(date_object_split[0]), "%Y-%m-%d") #Fix date for compare
        delta = thirty_days_from_date_added - user_date_added
        if delta.days <= 14 or m['subscription_status'] == 'active':        
            if m['email_alert_1']:
                email_list.append(m['email_alert_1'])
            if m['email_alert_2']:
                email_list.append(m['email_alert_2'])
            if m['email_alert_3']:
                email_list.append(m['email_alert_3'])
            if m['email_address']:
                email_list.append(m['email_address'])

    no_dupe_email = list(set(email_list))
    ## Check for daily notifications list

    list_create = True
    for i in no_dupe_email:
        cd = {
             "email_address": i,
             "create_source": "Contact",
             "list_memberships": [
            "d13d60d0-f256-11e8-b47d-fa163e56c9b0"
             ]
        }
        cresp = cc.create_contact(cd)
        cc_user_ids.append(cresp['contact_id'])

    # Check if list exists and set ID or pass
    cc_list = []
    cc_list_id = None
    cc_list = cc.get_lists()
    for c in cc_list['lists']:
        if c['name'] == title: #'Blake New List Temp Test':
            list_create = c['list_id']
    logger.debug(f"list_id: {list_create}")
    if list_create == True:
        cl = {
                "name": title,
                "description": f"List of Customers following {title}"
        }
        crl_resp = cc.create_lists(cl)
        add_member = {
                "source": {
            "contact_ids":
                cc_user_ids
                },
                "list_ids": [
                crl_resp['list_id']
                ]
        }
        cc_list_id = crl_resp['list_id']
        logger.debug(f"add-member: {add_member}")
        logger.debug(cc.add_list_memberships(add_member))
    else:
        add_member = {
                "source": {
            "contact_ids":
                cc_user_ids
                },
                "list_ids": [
                list_create
                ]
        }
        cc_list_id = list_create
        logger.debug(f"add-member: {add_member}")
        logger.debug(cc.add_list_memberships(add_member))
    suuid = shortuuid.uuid()
    ## Update or Create daily notifications list(add members)
    camp_name = f"{title} - {date_object[2]} {date_object[3]} - {suuid}"
    create_mail = {
        "name": camp_name,
        "email_campaign_activities": [{
                "format_type": 5,
                "from_email": "emily.taylor@bkwire.com",
                "from_name": "Emily Taylor",
                "reply_to_email": "emily.taylor@bkwire.com",
                "subject": sub_line,
                "html_content": html_output_creditor
        }]
    }

    # create Campaign BKWire Alert - Slug
    create_emails_resp = cc.create_emails(create_mail)
    logger.debug(create_emails_resp['campaign_activities'][0]['campaign_activity_id'])
    # update Camp with ListID
    update_mail = {
        "name": camp_name,
        "contact_list_ids": [cc_list_id],
        "current_status": "DRAFT",
        "format_type": 5,
        "from_email": "emily.taylor@bkwire.com",
        "from_name": "Emily Taylor",
        "reply_to_email": "emily.taylor@bkwire.com",
        "subject": sub_line,
        "html_content": html_output_creditor,
    }
    logger.debug(cc.update_emails(update_mail, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))
    # send email to list
    send_mail_now = {
        "scheduled_date": "0"
    }
    logger.info(cc.send_emails(send_mail_now, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))
    return '200'


def share_case(guid, **kwargs):
    logger.debug(f"share case kwargs: {kwargs}")
    cn = CaseNotify()
    cc_user_ids = []
    comment = ''
    bkw_dt = BkwDateTime()
    mysql_user_results = get_user_information(guid)
    date_object = bkw_dt.get_daily_time_w_month_day()
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_bk_query_share_case')
    out = template.render(dcid=kwargs['dcid'][0])
    output = run_sql_queries_no_cache(out)
    suuid = shortuuid.uuid()
    cc = ConstantContact()
    list_create = True
    cd = {
            "email_address": kwargs['email_address'][0],
            "create_source": "Contact",
            "list_memberships": [
                "d13d60d0-f256-11e8-b47d-fa163e56c9b0"
            ]
    }
    cresp = cc.create_contact(cd)
    cc_user_ids.append(cresp['contact_id'])

    # Check if list exists and set ID or pass
    cc_list = []
    cc_list_id = None
    cc_list = cc.get_lists()
    for c in cc_list['lists']:
        fix_list_name = c['name'].replace('case share -', '').strip()
        if fix_list_name == output[0][0]['case_name']:
            list_create = c['list_id']
    logger.debug(f"list_id: {list_create}")
    if list_create == True:
        cl = {
                "name": f"case share - {output[0][0]['case_name']}",
                "description": f"Case shared {output[0][0]['case_name']}"
        }
        crl_resp = cc.create_lists(cl)
        add_member = {
                "source": {
                "contact_ids":
                    cc_user_ids
                },
                "list_ids": [
                    crl_resp['list_id']
                ]
        }
        cc_list_id = crl_resp['list_id']
        logger.debug(f"add-member: {add_member}")
        logger.debug(cc.add_list_memberships(add_member))
    else:
        # Compare user_ids in list to that of notifications
        # Remove those not found in comp list
        # ID over to remove function
        add_member = {
                "source": {
            "contact_ids":
                cc_user_ids
                },
                "list_ids": [
                list_create
                ]
        }
        cc_list_id = list_create
        logger.debug(f"add-member: {add_member}")
        logger.debug(cc.add_list_memberships(add_member))

    ## Update or Create daily notifications list(add members)
    camp_name = f"Case Shared - {output[0][0]['case_name']} - {suuid}"
    sub_line = f"A case has been shared with you"
    load_case_resp = cn.load_case_sql_results(kwargs['dcid'][0])
    #html_output = cn.load_html_results_bk(load_case_resp, 'bkw_bankruptcy_shared_v2', mysql_user_results, kwargs['comment'][0])
    if kwargs['comment'][0] == '':
        pass
    else:
        comment = f"Note from [[FIRSTNAME]]: {kwargs['comment'][0]}"
        
    html_output = cn.load_html_results_bk(load_case_resp, 'bkw_bankruptcy_shared_v2', mysql_user_results, comment=comment)

    from_email = 'emily.taylor@bkwire.com'

    create_mail = {
        "name": camp_name,
        "email_campaign_activities": [{
                "format_type": 5,
                "from_email": from_email,
                "from_name": "Emily Taylor",
                "reply_to_email": from_email,
                "subject": sub_line,
                "html_content": html_output,
        }]
    }
    # create Campaign BKWire Alert - Slug
    create_emails_resp = cc.create_emails(create_mail)

    if create_emails_resp == None:
        return '500'
    else:
        logger.debug(f"Camp activity ID: {create_emails_resp['campaign_activities'][0]['campaign_activity_id']}")
        # update Camp with ListID
        update_mail = {
            "name": camp_name,
            "contact_list_ids": [cc_list_id],
            "current_status": "DRAFT",
            "format_type": 5,
            "from_email": from_email,
            "from_name": "Emily Taylor",
            "reply_to_email": from_email,
            "subject": sub_line,
            "html_content": html_output,
        }
        logger.debug(cc.update_emails(update_mail, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))
        # send email to list
        send_mail_now = {
            "scheduled_date": "0"
        }
        logger.info(cc.send_emails(send_mail_now, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))
        return '200'

def share_loss(guid, **kwargs):
    cn = CaseNotify()
    cc_user_ids = []
    bkw_dt = BkwDateTime()
    suuid = shortuuid.uuid()
    mysql_user_results = get_user_information(guid)    
    date_object = bkw_dt.get_daily_time_w_month_day()
    file_loader = FileSystemLoader('templates/sql')
    env = Environment(loader=file_loader)
    template = env.get_template('mysql_bk_query_share_loss')
    out = template.render(lossid=kwargs['lossid'][0])
    output = run_sql_queries_no_cache(out)

    cc = ConstantContact()
    list_create = True
    cd = {
            "email_address": kwargs['email_address'][0],
            "create_source": "Contact",
            "list_memberships": [
                "d13d60d0-f256-11e8-b47d-fa163e56c9b0"
            ]
    }
    cresp = cc.create_contact(cd)
    cc_user_ids.append(cresp['contact_id'])

    # Check if list exists and set ID or pass
    cc_list = []
    cc_list_id = None
    cc_list = cc.get_lists()
    for c in cc_list['lists']:
        fix_list_name = c['name'].replace('loss share -', '').strip()
        if fix_list_name == output[0][0]['creditor_name']:
            list_create = c['list_id']
    logger.debug(f"list_id: {list_create}")
    if list_create == True:
        cl = {
                "name": f"loss share - {output[0][0]['creditor_name']}",
                "description": f"Loss shared {output[0][0]['creditor_name']}"
        }
        crl_resp = cc.create_lists(cl)
        add_member = {
                "source": {
                "contact_ids":
                    cc_user_ids
                },
                "list_ids": [
                    crl_resp['list_id']
                ]
        }
        cc_list_id = crl_resp['list_id']
        logger.debug(f"add-member: {add_member}")
        logger.debug(cc.add_list_memberships(add_member))
    else:
        # Compare user_ids in list to that of notifications
        # Remove those not found in comp list
        # ID over to remove function
        add_member = {
                "source": {
            "contact_ids":
                cc_user_ids
                },
                "list_ids": [
                list_create
                ]
        }
        cc_list_id = list_create
        logger.debug(f"add-member: {add_member}")
        logger.debug(cc.add_list_memberships(add_member))

    ## Update or Create daily notifications list(add members)
    camp_name = f"Loss Shared - {output[0][0]['case_name']} - {suuid}"
    sub_line = f"An impacted business has been shared with you"

    if kwargs['comment'][0] == '':
        pass
    else:
        comment = f"Note from [[FIRSTNAME]]: {kwargs['comment'][0]}"
        
    html_output = cn.load_html_results_bk(output[0], 'bkw_loss_shared_v2', mysql_user_results, comment=comment)

    from_email = 'emily.taylor@bkwire.com'

    create_mail = {
        "name": camp_name,
        "email_campaign_activities": [{
                "format_type": 5,
                "from_email": from_email,
                "from_name": "Emily Taylor",
                "reply_to_email": from_email,
                "subject": sub_line,
                "html_content": html_output,
        }]
    }
    # create Campaign BKWire Alert - Slug
    create_emails_resp = cc.create_emails(create_mail)

    if create_emails_resp == None:
        return '500'
    else:
        logger.debug(f"Camp activity ID: {create_emails_resp['campaign_activities'][0]['campaign_activity_id']}")
        # update Camp with ListID
        update_mail = {
            "name": camp_name,
            "contact_list_ids": [cc_list_id],
            "current_status": "DRAFT",
            "format_type": 5,
            "from_email": from_email,
            "from_name": "Emily Taylor",
            "reply_to_email": from_email,
            "subject": sub_line,
            "html_content": html_output,
        }
        logger.debug(cc.update_emails(update_mail, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))
        # send email to list
        send_mail_now = {
            "scheduled_date": "0"
        }
        logger.info(cc.send_emails(send_mail_now, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))
        return '200'        

def main():
    bk_watch_list_report()
    comp_watch_list_report()

    #(list_losses(page=1, page_size=25, sort_column='creditor_name', sort_order='asc', search=None, industries=[], loss=[0, 0], id=20))
    #loss={'min': 500, 'max': 10000},
    #print(list_bankruptcies(page=1, page_size=25, sort_column='case_name', sort_order='asc', search='LLC', chapter_types=[11], industries=[], asset_ranges=[1,2], liability_ranges=[1,2], creditor_ranges=[1,3,4]))
    #create_user(first_name='Bob', last_name='Dole', email_address='samiam@mailinator.com', phone_number='555-555-2423', company_name='Sloan', company_state='MO', company_zip_code='63030', email_alerts_enabled=False, email_alert_1=None, email_alert_2=None, email_alert_3=None, text_alerts_enabled=False, phone_alert_1=None, phone_alert_2=None, phone_alert_3=None, is_social=False, auth0='Auth0|somecodehere', company_sector='29')
    #get_user('user_email=asdf@email.com')
    #print(view_bankruptcies(id=20))
    #print(view_pdf_form(id=20))
    #print(view_pacer_docket(id=[4124]))
    #update_user(259, company_zip_code='72450', phone_number='8675309')
    #add_notification_subscription('rando-bk', 0)
    #print(list_cities(state_code='AR'))
    #daily_bk_report()
    #create_team_user(userid=194, member_email_address='rachel.perry04@gmail.com')
    #generate_bk_digest('daily', 'Daily BKWire Digest', 'Todays notable Corp BKs')
    #cc = ConstantContact()
    #print(cc.get_lists())
    #print(cc.create_lists(cl))
    #print(cc.get_users(blake))
    #print(cc.add_list_memberships(add_member))
    #print(cc.get_emails())
    #print(cc.create_emails(create_mail))
    #print(cc.update_emails(update_mail, '41962145-245b-4b94-9dda-cd1a19d6691d'))
    #print(cc.send_emails(send_mail_now, '41962145-245b-4b94-9dda-cd1a19d6691d'))
    #token = auth0_managment_api_key()
    #pacer_data_results = {"Dexter Group Investments, Inc.": {"case_number": "6:2022bk04113", "court_id": "flmb", "date_filed": "2022-11-18", "cs_number": 4113, "cs_office": 6, "cs_chapter": 11, "case_link": "https://ecf.flmb.uscourts.gov/cgi-bin/iqquerymenu.pl?1351844", "pdf_dl_status": None, "bkw_files_id": 347, "skip_201_parse": True, "skip_204_parse": False, "docket_table": ["11/18/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085438211:bkwsplit:8:bkwsplit:None:bkwsplit:  *Voluntary Petition under Chapter 11. SubchapterV. (Fee Paid.).  Schedules and Statements Incomplete, Statement of Financial Affairs Not Filed or Incomplete, Disclosure of Compensation of Attorney Not Filed or Not Required,  Filed by Justin M Luna on behalf of Dexter Group Investments, Inc.. Chapter 11 Plan Subchapter V Due by 02/16/2023. (Luna, Justin) (Entered: 11/18/2022):bkwsplit:None", "11/18/2022:bkwsplit:None:bkwsplit:None:bkwsplit:None:bkwsplit:  Receipt of Filing Fee for Voluntary Petition (Chapter 11)( 6:22-bk-04113) [misc,volp11a2] (1738.00). Receipt Number A71288474, Amount Paid $1738.00 (U.S. Treasury) (Entered: 11/18/2022):bkwsplit:None", "11/18/2022:bkwsplit:None:bkwsplit:None:bkwsplit:None:bkwsplit:  Debtor(s) Attorney and Unrepresented Debtor(s) are directed to comply with all requirements set forth in Local Rule 2081-1. The Court's Local Rule can be found at http://www.flmb.uscourts.gov/localrules/rules/2081-1.pdf. (ADIclerk) (Entered: 11/18/2022):bkwsplit:None", "11/18/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085459229:bkwsplit:1:bkwsplit:None:bkwsplit:  Statement of Corporate Ownership.  Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc.. (Rutha) (Entered: 11/23/2022):bkwsplit:None", "11/21/2022:bkwsplit:None:bkwsplit:None:bkwsplit:None:bkwsplit:  Assignment of the Honorable Grace E. Robson, Bankruptcy Judge to this case . (Lisa P.) (Entered: 11/21/2022):bkwsplit:None", "11/21/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085446756:bkwsplit:3:bkwsplit:None:bkwsplit:  Order Prescribing Procedures in Chapter 11 Subchapter V Case, Setting Deadline for Filing Plan, and Setting Status Conference  (related document(s)1). Hearing scheduled for 1/10/2023 at 10:00 AM at Orlando, FL - Courtroom 6D, 6th Floor, George C. Young Courthouse, 400 W. Washington Street. Service Instructions: Clerks Office to serve. (Rutha) (Entered: 11/21/2022):bkwsplit:None", "11/21/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085449803:bkwsplit:1:bkwsplit:None:bkwsplit:  Notice of Appearance and Request for Notice  Filed by Kenneth D Herron Jr on behalf of Creditor Alicia Kilburn. (Herron, Kenneth) (Entered: 11/21/2022):bkwsplit:None", "11/22/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085451444:bkwsplit:1:bkwsplit:None:bkwsplit:  Notice of Appearance Filed by Bryan E Buenaventura on behalf of U.S. Trustee United States Trustee - ORL. (Buenaventura, Bryan) (Entered: 11/22/2022):bkwsplit:None", "11/22/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085453803:bkwsplit:877:bkwsplit:None:bkwsplit:  Notice of Appointment of Chapter 11, Subchapter V Trustee and Verified Statement of Aaron R. Cohen. Aaron R. Cohen added to the case. Meeting of Creditors scheduled for December 19, 2022 at 10:00 a.m. in Room The meeting of creditors will be held telephonically on December 19, 2022 at 10:00 a.m. The telephone conference line is (877) 801-2055; the participant passcode is 8940738#. Filed by Bryan E Buenaventura on behalf of U.S. Trustee United States Trustee - ORL. (Buenaventura, Bryan) (Entered: 11/22/2022):bkwsplit:None", "11/23/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085458909:bkwsplit:2:bkwsplit:None:bkwsplit:  Notice of Bankruptcy Case . Section 341(a) meeting to be held on 12/19/2022 at 10:00 AM. U.S. Trustee (Orl) will hold the meeting telephonically. Call in Number: 877-801-2055. Passcode: 8940738#. Proofs of Claims due by 1/27/2023. (Rutha) (Entered: 11/23/2022):bkwsplit:None", "11/23/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085459188:bkwsplit:2:bkwsplit:None:bkwsplit:  Notice of Deficient Filing. Summary of Assets, Schedules, Statement of Financial Affairs, Statement of Current Monthly Income, Case Management Summary and Disclosure of Compensation  (related document(s)1). (Rutha) (Entered: 11/23/2022):bkwsplit:None", "11/23/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085477841:bkwsplit:5:bkwsplit:None:bkwsplit:  BNC Certificate of Mailing - Order (related document(s) (Related Doc # 2)). Notice Date 11/23/2022. (Admin.) (Entered: 11/29/2022):bkwsplit:None", "11/25/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085466530:bkwsplit:4:bkwsplit:None:bkwsplit:  BNC Certificate of Mailing - Notice of Meeting of Creditors. (related document(s) (Related Doc # 6)). Notice Date 11/25/2022. (Admin.) (Entered: 11/26/2022):bkwsplit:None", "11/25/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085466531:bkwsplit:3:bkwsplit:None:bkwsplit:  BNC Certificate of Mailing - Notice to Creditors and Parties in Interest (related document(s) (Related Doc # 7)). Notice Date 11/25/2022. (Admin.) (Entered: 11/26/2022):bkwsplit:None", "11/28/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085469336:bkwsplit:1:bkwsplit:None:bkwsplit:  Notice of Appearance and Request for Notice  Filed by U.S. Trustee United States Trustee - ORL. (Aleskovsky, Audrey) (Entered: 11/28/2022):bkwsplit:None", "11/28/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085473559:bkwsplit:4:bkwsplit:None:bkwsplit:  Chapter 11 Case Management Summary  Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc.. (Luna, Justin) (Entered: 11/28/2022):bkwsplit:None", "12/02/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085501258:bkwsplit:4:bkwsplit:2:bkwsplit:  Motion to Extend Deadline to File Schedules and Statements  Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc. (Attachments: # 1 Mailing Matrix) (Luna, Justin) (Entered: 12/02/2022):bkwsplit:[[], [('https://ecf.flmb.uscourts.gov/doc1/046185501259', 'Mailing Matrix) Luna, Justin) Entered: 12/02/2022)')]]", "12/02/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085504670:bkwsplit:4:bkwsplit:None:bkwsplit:  Application to Employ Justin M. Luna and the Law Firm of Latham, Luna, Eden  Beaudine, LLP as Counsel for the Debtor  Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc. (Luna, Justin) (Entered: 12/02/2022):bkwsplit:None", "12/02/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085504698:bkwsplit:3:bkwsplit:None:bkwsplit:  Verified Statement Pursuant to Rule 2014 of the Federal Rules of Bankruptcy Procedure in Support of the Application of Dexter Group Investments, Inc., to Employ Justin M. Luna and the Law Firm of Latham, Luna, Eden  Beaudine, LLP, as Debtor's Counsel as of November 18, 2022 Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc. (related document(s)15). (Luna, Justin) (Entered: 12/02/2022):bkwsplit:None", "12/02/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085504715:bkwsplit:3:bkwsplit:None:bkwsplit:  Statement of Justin M. Luna and Latham, Luna, Eden  Beaudine, LLP, Pursuant to 11 U.S.C. \u00a7 329(a) and Rule 2016(b) of the Federal Rules of Bankruptcy Procedure Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc. (related document(s)15). (Luna, Justin) (Entered: 12/02/2022):bkwsplit:None", "12/05/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085511351:bkwsplit:2:bkwsplit:None:bkwsplit:  Order Granting Motion To Extend Deadline to File Schedules and Statements Until December 9, 2022 (Related Doc # 14) Service Instructions: Justin Luna is directed to serve a copy of this order on interested parties and file a proof of service within 3 days of entry of the order. (Vivianne) (Entered: 12/05/2022):bkwsplit:None", "12/05/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085512000:bkwsplit:2:bkwsplit:2:bkwsplit:  Proof of Service of Order Granting Motion to Extend Time to File Schedules and Statement of Financial Affairs.  Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc. (related document(s)18). (Attachments: # 1 Mailing Matrix) (Luna, Justin) (Entered: 12/05/2022):bkwsplit:[[], [('https://ecf.flmb.uscourts.gov/doc1/046185512001', 'Mailing Matrix) Luna, Justin) Entered: 12/05/2022)')]]", "12/09/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085541057:bkwsplit:26:bkwsplit:None:bkwsplit:  Schedules A - H, Includes addition or deletion of creditors to Schedules or Change in the Amount or Classification of Debts. Statement of Financial Affairs, Amended Verification of Creditor Matrix (Fee Paid.) Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc.. (Luna, Justin) (Entered: 12/09/2022):bkwsplit:None", "12/09/2022:bkwsplit:None:bkwsplit:None:bkwsplit:None:bkwsplit:  Receipt of Filing Fee for Schedules (all schedules, individual schedules or amended schedules)( 6:22-bk-04113-GER) [misc,schaja] ( 32.00). Receipt Number A71420364, Amount Paid $ 32.00 (U.S. Treasury) (Entered: 12/09/2022):bkwsplit:None", "12/12/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085545823:bkwsplit:2:bkwsplit:None:bkwsplit:  Notice of Filing RE: The Federal Tax Returns, Balance Sheet and Profit Loss Statement Described in the Disclosure Section have Not been Prepared Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc.. (Luna, Justin) Modified on 12/13/2022 (Ryan). (Entered: 12/12/2022):bkwsplit:None", "12/12/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085546513:bkwsplit:2:bkwsplit:None:bkwsplit:  Notice of Deficient Filing. Service on additional creditors  (related document(s)20). (Cathy P.) (Entered: 12/12/2022):bkwsplit:None", "12/12/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085547911:bkwsplit:1:bkwsplit:None:bkwsplit:  Notice of Additional Creditors Re: Purchase of Tax Liens - Brevard County Tax year 2020 account # 2425967- 10 Stone St Cocoa, FL 32922 Filed by Creditor Brevard County Tax Collector. (Brevard County Tax Collector (AB)) (Entered: 12/12/2022):bkwsplit:None", "12/12/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085547926:bkwsplit:1:bkwsplit:None:bkwsplit:  Notice of Additional Creditors Re: Purchase of Tax Liens - Brevard County Tax year 2021 account # 2425967- 10 Stone St Cocoa, FL 32922. Filed by Creditor Brevard County Tax Collector. (Brevard County Tax Collector (AB)) (Entered: 12/12/2022):bkwsplit:None", "12/12/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085548003:bkwsplit:4:bkwsplit:None:bkwsplit:  Notice of 2004 Examination of Debtor/Dexter Group Investments, Inc.. (Documents Only) Filed by Kenneth D Herron Jr on behalf of Creditor Alicia Kilburn. (Herron, Kenneth) (Entered: 12/12/2022):bkwsplit:None", "12/12/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085548866:bkwsplit:1:bkwsplit:None:bkwsplit:  Proof of Service of Notice of Chapter 11 Bankruptcy Case Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc. (related document(s)24, 23, 22, 6). (Luna, Justin) (Entered: 12/12/2022):bkwsplit:None", "12/14/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085558018:bkwsplit:8:bkwsplit:None:bkwsplit:  Application to Employ John Cullen, CPA and Duerr  Cullen CPAs, P.A. as Accountant for the Debtor  Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc. (Luna, Justin) (Entered: 12/14/2022):bkwsplit:None", "12/14/2022:bkwsplit:None:bkwsplit:None:bkwsplit:None:bkwsplit:  The Application to Employ/Retain (Doc 27) appears to be the type of motion or application listed on the Court's Accompanying Orders List posted on the Court's website (Click here to view). Local Rule 9072-1(b)(1) states that if a motion or application is listed on the Accompanying Orders List, counsel may submit a proposed order at the time that the motion or application is filed. Counsel for the moving party is directed to verify that the motion or application is listed on the Accompanying Orders List, and if so, to submit a proposed order granting the motion or approving the application. (ADIclerk) (Entered: 12/14/2022):bkwsplit:None", "12/15/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085565731:bkwsplit:2:bkwsplit:None:bkwsplit:  Order Approving Application to Employ/Retain Justin M. Luna and the Law Firm of Latham, Luna, Eden  Beaudine, LLP as Counsel for the Debtor as of November 18, 2022 (Related Doc # 15). Service Instructions: Justin Luna is directed to serve a copy of this order on interested parties and file a proof of service within 3 days of entry of the order. (Rutha) (Entered: 12/15/2022):bkwsplit:None", "12/15/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085566114:bkwsplit:1:bkwsplit:None:bkwsplit:  Order Establishing Procedures for Video Hearings and Registration Link to Appear via Zoom. Service Instructions: Clerks Office to serve. NG -(ADIclerk) (Entered: 12/15/2022):bkwsplit:None", "12/15/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085566501:bkwsplit:1:bkwsplit:None:bkwsplit:  Proof of Service of Order Approving Application to Employ Justin M. Luna and Latham Luna Eden  Beaudine, LLP as Counsel for the Debtor as of November 18, 2022.  Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc. (related document(s)28). (Luna, Justin) (Entered: 12/15/2022):bkwsplit:None", "12/15/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085568816:bkwsplit:2:bkwsplit:None:bkwsplit:  Order Approving Application to Employ/Retain John Cullen and Duerr  Cullen CPA's, PA as Accountant for the Debtor (Related Doc # 27). Service Instructions: Justin Luna is directed to serve a copy of this order on interested parties and file a proof of service within 3 days of entry of the order. (Deborah K.) (Entered: 12/15/2022):bkwsplit:None", "12/16/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085574033:bkwsplit:1:bkwsplit:None:bkwsplit:  Proof of Service of Order Approving Application to Employ John Cullen, CPA and Duerr  Cullen CPAs, P.A. as Accountant for the Debtor.  Filed by Justin M Luna on behalf of Debtor Dexter Group Investments, Inc. (related document(s)31). (Luna, Justin) (Entered: 12/16/2022):bkwsplit:None", "12/17/2022:bkwsplit:https://ecf.flmb.uscourts.gov/doc1/046085578734:bkwsplit:3:bkwsplit:None:bkwsplit:  BNC Certificate of Mailing - PDF Document. (related document(s) (Related Doc # 29)). Notice Date 12/17/2022. (Admin.) (Entered: 12/18/2022):bkwsplit:None", "12/19/2022:bkwsplit:None:bkwsplit:None:bkwsplit:None:bkwsplit:  The United States Trustee states that the initial meeting of creditors was held and concluded on December 19, 2022. Filed by U.S. Trustee United States Trustee - ORL. (Buenaventura, Bryan) (Entered: 12/19/2022):bkwsplit:None"], "pdf_dl_skip": False, "pdf_dl_status_201": "complete", "pdf_dl_status_204206": None, "company_address": "1442 e. lincoln avenue", "company_city": "orange", "company_state": "ca", "company_zip": "92865", "company_industry": "Unknown", "pdf_doc_files": ["flmb.2022bk04113.1351844-petition.pdf"], "case_name": "Dexter Group Investments, Inc.", "parse_201_attempt": False, "parse_204206_attempt": True, "Alicia Kilburn 2290 W Eau Gallie Blvd. Suite 212 Melbourne, FL 32935 __QJRw4N4Js8mBQ8DgBDdTEf__": {"creditor_phone": [], "creditor_email": [], "creditor_company_name": "alicia kilburn", "creditor_company_state": "fl", "creditor_company_zip": "32935", "nature_of_claim": "Judgment ", "unsecured_claim_value": "1287042.18 ", "industry": None}, "Brevard County Tax Collector 400 South Street, 6th Floor FL 32780 __F8C5YXifa4BuCzZDe5ruLU__": {"creditor_phone": [], "creditor_email": [], "creditor_company_name": "brevard county tax collector", "creditor_company_state": None, "creditor_company_zip": "32780", "nature_of_claim": "Property Taxes ", "unsecured_claim_value": "51047.26 ", "industry": None}, "Pejman Jamshiddanaee 19 Welham Road London, N144FB, UK __DqTGYq659zHqoU4S9uqGKp__": {"creditor_phone": [], "creditor_email": [], "creditor_company_name": "Pejman Jamshiddanaee", "creditor_company_state": None, "creditor_company_zip": "n144fb", "nature_of_claim": "Loan ", "unsecured_claim_value": "502000.00 ", "industry": None}, "dci_id": 4009, "bkw_filing_id": "3818"}}
    #check_missing_204_data(pacer_data_results)
    #print(token)
    #create_user_constant_contact(259, company_zip_code='72450', phone_number='8675309')

# MAIN
if __name__ == '__main__':
    main()
