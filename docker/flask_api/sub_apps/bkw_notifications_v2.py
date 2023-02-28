import os,sys
import shortuuid
import logging.config
from logtail import LogtailHandler
from os import listdir, path
from jinja2 import Environment, FileSystemLoader
## IMPORT CUSTOM MODULES ##
sys.path.insert(0, '/app')
from modules.pacer.pacer_api_v3 import PacerApiSvc
from modules.database.db_select import dbSelectItems
from modules.bkwdatetime.date_time import BkwDateTime
from modules.notifications.bkw_constantcontact import ConstantContact
from modules.parsers.parse_results_download_pdf import ResultsParserSvc
from modules.database.db_connec_v2 import insert_docket_data, db_login
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

class CaseNotify:
    def __init__(self):
        self.bkw_dt = BkwDateTime()
        self.db1 = dbSelectItems()
        self.db1.db_login()

    def notify_todays_loss_company(self):
        # SQL Template / jinja2
        notify_comp_dict = {}
        notify_comp_list = []
        date_object = self.bkw_dt.get_daily_time_w_month_day()
        bk_file_loader = FileSystemLoader('templates/sql')
        bk_env = Environment(loader=bk_file_loader)
        bk_template = bk_env.get_template('mysql_loss_query_newly_added')
        bk_output = bk_template.render(sdf=date_object[1], edf=date_object[1])
        #bk_output = bk_template.render(sdf='2022-07-13', edf='2022-07-13')
        bk_mysql_results = self.db1.fetch_no_cache(bk_output)

        # With our results - lets check against all watchlist entries
        bk_template_watch = bk_env.get_template('mysql_comp_watchlist_get_all_distinct')
        bk_output_watch = bk_template_watch.render()
        bk_mysql_results_watch = self.db1.fetch_no_cache(bk_output_watch)
        logger.debug(f"bk_mysql_results_watch: {bk_mysql_results_watch}")
        if bk_mysql_results != None:
            for i in bk_mysql_results:
                if self.search(bk_mysql_results_watch, 'comp_slug', i['slug']):
                    # append dic to list
                    notify_comp_dict[i['slug']] = 1
                    notify_comp_list.append({"slug": i['slug'], "dci_id": i['dci_id'], "name": i['creditor_name']})
                    logger.debug(F"sending notification for: {i['slug']}")
                else:
                    pass
        else:
            logger.warning(f"No new loss data detected!")

        self.build_company_topic(notify_comp_dict, notify_comp_list)

    def notify_bankruptcies(self):
        # SQL Template / jinja2
        date_object = self.bkw_dt.get_daily_time_w_month_day()
        bk_file_loader = FileSystemLoader('templates/sql')
        bk_env = Environment(loader=bk_file_loader)
        bk_template = bk_env.get_template('mysql_bk_watchlist_get_all')
        bk_output = bk_template.render()
        bk_mysql_results = self.db1.fetch_no_cache(bk_output)

        pas = PacerApiSvc()
        pacer_login_session = None
        cookie_check = pas.pacer_check_cookie()
        if cookie_check == 'expired':
            pacer_login_session = pas.pacer_session_login()
            pas.pacer_cso_login()
        else:
            logger.debug('cookies still valid')
            pacer_login_session = cookie_check

        for b in bk_mysql_results:
            logger.debug(f"PACER CASE UPDATE: {b['case_link']} {b['case_number']}")
            pas.pacer_dkt_rpt(b['case_link'])
            pacer_html_results, pls = pas.pacer_post_for_html(b['case_link'], b['case_number'], b['date_filed'])
            rps = ResultsParserSvc(pls)
            html_dic_results = rps.parse_html_table_to_dic(b['case_name'], pacer_html_results)
            # THINK WERE MISSING A STEP 
            docket_table_results = rps.docket_table_parse(html_dic_results[b['case_name']]['docket_table'])
            html_dic_results[b['case_name']]['docket_table'] = docket_table_results
            html_dic_results[b['case_name']]['dci_id'] = b['dci_id']
            html_dic_results[b['case_name']]['status_204206'] = b['status_204206']
            conn = db_login()
            insert_docket_data(conn, html_dic_results)
        self.html_d_res = html_dic_results
        self.build_bk_topic()

    def build_company_topic(self, notify_comp_dict, notify_comp_list):

        bk_file_loader = FileSystemLoader('templates/sql')
        bk_env = Environment(loader=bk_file_loader)
        bk_template = bk_env.get_template('mysql_comp_watchlist_get_user_info')

        for nd in notify_comp_dict:
            user_ids = []
            dcid_list = []
            email_list = []
            for n in notify_comp_list:
                if n['slug'] == nd:
                    dcid_list.append(n['dci_id'])
                    notify_comp_dict[nd] = {}
                    notify_comp_dict[nd]['cname'] = n['name']
                    notify_comp_dict[nd]['dcid'] = dcid_list
            bk_output = bk_template.render(comp_slug=nd)
            bk_mysql_results = self.db1.fetch_no_cache(bk_output)
            for m in bk_mysql_results:
                if m['email_alert_1']:
                    email_list.append(m['email_alert_1'])
                if m['email_alert_2']:
                    email_list.append(m['email_alert_2'])
                if m['email_alert_3']:
                    email_list.append(m['email_alert_3'])
                if m['email_address']:
                    email_list.append(m['email_address'])
                user_ids.append(m['user_id'])
            no_dupe_list = list(set(email_list))
            notify_comp_dict[nd]['elist'] = no_dupe_list
            notify_comp_dict[nd]['uids'] = user_ids

        logger.debug(f"NCD: {notify_comp_dict}")
        self.notify_company_topic(notify_comp_dict)

    def notify_company_topic(self, ncd):
        cc = ConstantContact()
        date_object = self.bkw_dt.get_daily_time_w_month_day()
        suuid = shortuuid.uuid()
        for i in ncd:
            ulist = []
            for e in ncd[i]['elist']:
                cd = {
                  "email_address": e,
                  "create_source": "Contact",
                  "list_memberships": [
                    "d13d60d0-f256-11e8-b47d-fa163e56c9b0"
                  ]
                }
                cresp = cc.create_contact(cd)
                ulist.append(cresp['contact_id'])
            ncd[i]['ulist'] = ulist
            ncd[i]['list_create'] = True

        # Check if list exists and set ID or pass
        cc_list = cc.get_lists()
        for c in cc_list['lists']:
            create_list_slug = c['name'].replace('BKWire Alert','').strip()
            create_list_slug = create_list_slug.replace(' ', '-').lower()
            create_list_slug = create_list_slug.replace(f"{date_object[2]} {date_object[3]}", '').strip()

            if create_list_slug in ncd.keys():
                logger.info(f'update list')
                ncd[create_list_slug]['list_create'] = c['list_id']
            else:
                pass
        # Create list or update if exists
        logger.debug(f"NCD_nct: {ncd}")
        for n in ncd:
            logger.debug(ncd)
            for u in ncd[n]['uids']:
                for i in ncd[n]['dcid']:
                    self.insert_user_notifications(u, f"New Loss Activity", \
                    f"New loss for company: {ncd[n]['cname']}", 'loss', i, i)#loss_id)

            if ncd[n]['list_create'] == True:
                cl = {
                  "name": f"BKWire Alert {n}",
                  "description": f"List of Customers following {n}"
                }
                crl_resp = cc.create_lists(cl)
                add_member = {
                  "source": {
                    "contact_ids":
                        ncd[n]['ulist']
                  },
                  "list_ids": [
                    crl_resp['list_id']
                  ]
                }
                ncd[n]['list_create'] = crl_resp['list_id']
                logger.debug(f"add_member: {add_member}")
                logger.debug(cc.add_list_memberships(add_member))
            else:
                # Compare user_ids in list to that of notifications
                # Remove those not found in comp list
                # ID over to remove function
                add_member = {
                  "source": {
                    "contact_ids":
                        ncd[n]['ulist']
                  },
                  "list_ids": [
                    ncd[n]['list_create']
                  ]
                }
                logger.debug(f"add_member: {add_member}")
                logger.debug(cc.add_list_memberships(add_member))

            loss_sql_resp = self.load_loss_sql_results(ncd[n]['cname'])
            logger.debug(f"Loss SQL Resp: {loss_sql_resp}")
            load_html_resp = self.load_html_results_comp(ncd[n]['cname'], loss_sql_resp)
            logger.debug(f"HTML SQL Resp: {load_html_resp}")
            # HTML content generated from templates
            camp_name = f"BKWire Alert - {ncd[n]['cname']} - {date_object[2]} {date_object[3]} - {suuid}"

            create_mail = {
                "name": camp_name,
                "email_campaign_activities": [{
                        "format_type": 5,
                        "from_email": "emily.taylor@bkwire.com",
                        "from_name": "Emily Taylor",
                        "reply_to_email": "emily.taylor@bkwire.com",
                        "subject": f"BKWire Alert - {ncd[n]['cname']}",
                        "html_content": load_html_resp,
                }]
            }
            logger.debug(f"Create mail: {create_mail}")
            # create Campaign BKWire Alert - Slug
            create_emails_resp = cc.create_emails(create_mail)

            if create_emails_resp == None:
                pass
            else:
                logger.debug(f"Camp activity ID: {create_emails_resp['campaign_activities'][0]['campaign_activity_id']}")
                # update Camp with ListID
                update_mail = {
                    "name": camp_name,
                    "contact_list_ids": [ncd[n]['list_create']],
                    "current_status": "DRAFT",
                    "format_type": 5,
                    "from_email": "emily.taylor@bkwire.com",
                    "from_name": "Emily Taylor",
                    "reply_to_email": "emily.taylor@bkwire.com",
                    "subject": f"BKWire Alert - {ncd[n]['cname']}",
                    "html_content": load_html_resp,
                }
                logger.debug(f"Update mail: {update_mail}")
                logger.debug(cc.update_emails(update_mail, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))
                # send email to list
                send_mail_now = {
                    "scheduled_date": "0"
                }
                logger.info(cc.send_emails(send_mail_now, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))

    def build_bk_topic(self, case_refresh=None):
        logger.debug(f"running build_bk_topic: case_refresh={case_refresh}")
        bkdt = BkwDateTime()
        notify_bk_list = []
        notify_bk_dict = {}

        bk_file_loader = FileSystemLoader('templates/sql')
        bk_env = Environment(loader=bk_file_loader)
        date_today = bkdt.get_timestamp_day_now_entry()
        monday = bkdt.get_timestamp_day_monday_of_week()
        if case_refresh == None:
            bk_template = bk_env.get_template('mysql_notify_topic_bks')
            bk_output = bk_template.render(entry_date_start=date_today)
        else:
            bk_template = bk_env.get_template('mysql_notify_topic_bks_refresh')
            bk_output = bk_template.render(entry_date_start=date_today, case_refresh=case_refresh)

        bk_mysql_results = self.db1.fetch_no_cache(bk_output)
        bk_templ_update_notify = bk_env.get_template('mysql_bk_watchlist_get_user_info')
        for bk in bk_mysql_results:
            user_ids = []
            dcid_list = []
            email_list = []
            notify_bk_dict[bk['dci_id']] = {}
            notify_bk_dict[bk['dci_id']]['case_name'] = bk['case_name']
            notify_bk_dict[bk['dci_id']]['case_number'] = bk['case_number']
            notify_bk_dict[bk['dci_id']]['filing_date'] = bk['filing_date']
            notify_bk_dict[bk['dci_id']]['court_name_district'] = bk['court_name_district']            
            bk_output_up_notify = bk_templ_update_notify.render(dc_id=bk['dci_id'], price_id=os.environ['STRIPE_MVP_PRICE_ID'])
            bk_mysql_results_up_notify = self.db1.fetch_no_cache(bk_output_up_notify)
            for ubk in bk_mysql_results_up_notify:
                if ubk['email_alert_1']:
                    email_list.append(ubk['email_alert_1'])
                if ubk['email_alert_2']:
                    email_list.append(ubk['email_alert_2'])
                if ubk['email_alert_3']:
                    email_list.append(ubk['email_alert_3'])
                if ubk['email_address']:
                    email_list.append(ubk['email_address'])
                user_ids.append(ubk['user_id'])

            no_dupe_list = list(set(email_list))
            notify_bk_dict[bk['dci_id']]['elist'] = no_dupe_list
            notify_bk_dict[bk['dci_id']]['uids'] = user_ids
        self.notify_bk_topic(notify_bk_dict)

    def notify_bk_topic(self, notify_bk_dict):
        logger.debug(f"running notify_bk_topic: {notify_bk_dict}")
        cd = None
        cc = ConstantContact()
        suuid = shortuuid.uuid()
        date_object = self.bkw_dt.get_daily_time_w_month_day()
        if notify_bk_dict:
            for i in notify_bk_dict:
                ulist = []
                if 'elist' in notify_bk_dict[i]:
                    if len(notify_bk_dict[i]['elist']) > 0:
                        for e in notify_bk_dict[i]['elist']:
                            cd = {
                            "email_address": e,
                            "create_source": "Contact",
                            "list_memberships": [
                                "d13d60d0-f256-11e8-b47d-fa163e56c9b0"
                            ]
                            }
                            cresp = cc.create_contact(cd)
                            ulist.append(cresp['contact_id'])
                        notify_bk_dict[i]['ulist'] = ulist
                        notify_bk_dict[i]['list_create'] = True
                else:
                    logger.info("notify_bk_topic: Nothing to notify")
                    return
        else:
            logger.info("notify_bk_topic: Nothing to notify")
            return

        if cd == None:
            logger.info("notify_bk_topic: Nothing to notify")
            return
        else:
            # Check if list exists and set ID or pass
            cc_list = cc.get_lists()
            for c in cc_list['lists']:
                create_list_slug = c['name'].replace('BKWire Alert','').strip()
                create_list_slug = create_list_slug.replace(f"{date_object[2]} {date_object[3]}", '').strip()
                try:
                    if int(create_list_slug) in notify_bk_dict.keys():
                        logger.info(f'update list')
                        notify_bk_dict[int(create_list_slug)]['list_create'] = c['list_id']
                    else:
                        pass
                except:
                    pass
            # Create list or update if exists
            for n in notify_bk_dict:
                logger.debug(notify_bk_dict)
                for u in notify_bk_dict[n]['uids']:
                    self.insert_user_notifications(u, f"New Case Activity", \
                    f"New Case Activity: {notify_bk_dict[n]['case_name']}", 'bk', n, None)#loss_id)

                if notify_bk_dict[n]['list_create'] == True:
                    cl = {
                    "name": f"BKWire Alert {n}",
                    "description": f"List of Customers following {notify_bk_dict[n]['case_name']}"
                    }
                    crl_resp = cc.create_lists(cl)
                    add_member = {
                    "source": {
                        "contact_ids":
                            notify_bk_dict[n]['ulist']
                    },
                    "list_ids": [
                        crl_resp['list_id']
                    ]
                    }
                    notify_bk_dict[n]['list_create'] = crl_resp['list_id']
                    logger.debug(cc.add_list_memberships(add_member))
                else:
                    # Compare user_ids in list to that of notifications
                    # Remove those not found in comp list
                    # ID over to remove function
                    add_member = {
                    "source": {
                        "contact_ids":
                            notify_bk_dict[n]['ulist']
                    },
                    "list_ids": [
                        notify_bk_dict[n]['list_create']
                    ]
                    }
                    logger.debug(cc.add_list_memberships(add_member))

                camp_name = f"BKWire Alert - {notify_bk_dict[n]['case_name']} - {date_object[2]} {date_object[3]} - {suuid}"
                load_html_resp = self.load_html_results_bk(notify_bk_dict, 'bkw_bankruptcy_notification_v2')
                # HTML content generated from templates
                logger.debug(load_html_resp)
                if notify_bk_dict[n]['ulist'] == 0:
                    pass
                else:
                    create_mail = {
                        "name": camp_name,
                        "email_campaign_activities": [{
                                "format_type": 5,
                                "from_email": "emily.taylor@bkwire.com",
                                "from_name": "Emily Taylor",
                                "reply_to_email": "emily.taylor@bkwire.com",
                                "subject": f"BKWire Alert - {notify_bk_dict[n]['case_name']}",
                                "html_content": load_html_resp,
                        }]
                    }
                    # create Campaign BKWire Alert - Slug
                    create_emails_resp = cc.create_emails(create_mail)
                    if create_emails_resp == None:
                        logger.warning(f"Alert email address list empty - {notify_bk_dict[n]['case_name']}")
                    else:
                        logger.debug(create_emails_resp['campaign_activities'][0]['campaign_activity_id'])
                        # update Camp with ListID
                        update_mail = {
                            "name": camp_name,
                            "contact_list_ids": [notify_bk_dict[n]['list_create']],
                            "current_status": "DRAFT",
                            "format_type": 5,
                            "from_email": "emily.taylor@bkwire.com",
                            "from_name": "Emily Taylor",
                            "reply_to_email": "emily.taylor@bkwire.com",
                            "subject": f"BKWire Alert - {notify_bk_dict[n]['case_name']}",
                            "html_content": load_html_resp,
                        }
                        logger.debug(cc.update_emails(update_mail, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))
                        # send email to list
                        send_mail_now = {
                            "scheduled_date": "0"
                        }
                        logger.info(cc.send_emails(send_mail_now, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))

    def notify_bk_topic_creditors(self, notify_bk20x_list, notify_bk_dict, loss_mysql_results):
        logger.debug(f"notify_bk_topic_creditors triggered: {notify_bk20x_list}")
        logger.debug(f"check notify_bk_dict: {notify_bk_dict}")
        cc = ConstantContact()
        suuid = shortuuid.uuid()
        date_object = self.bkw_dt.get_daily_time_w_month_day()
        if notify_bk20x_list:
            logger.debug(f"notify_bk20x_list exists!")
            for i in notify_bk20x_list:
                ulist = []
                if 'elist' in notify_bk_dict[i]:
                    for e in notify_bk_dict[i]['elist']:
                        logger.debug(f"notify_bk20x_list looping e: {e}")
                        cd = {
                        "email_address": e,
                        "create_source": "Contact",
                        "list_memberships": [
                            "d13d60d0-f256-11e8-b47d-fa163e56c9b0"
                        ]
                        }
                        cresp = cc.create_contact(cd)
                        ulist.append(cresp['contact_id'])
                    notify_bk_dict[i]['ulist'] = ulist
                    notify_bk_dict[i]['list_create'] = True
                else:
                    logger.debug(f"No ELIST found!")

            # Check if list exists and set ID or pass
            cc_list = cc.get_lists()
            for c in cc_list['lists']:
                logger.debug(f"looping c: {c}")
                create_list_slug = c['name'].replace('BKWire Alert Creditors','').strip()
                create_list_slug = create_list_slug.replace(f"{date_object[2]} {date_object[3]}", '').strip()
                try:
                    if int(create_list_slug) in notify_bk_dict.keys():
                        logger.info(f'update list')
                        notify_bk_dict[int(create_list_slug)]['list_create'] = c['list_id']
                    else:
                        pass
                except Exception as e:
                    logger.error(f"cc_list try failed: {e}")

            # Create list or update if exists
            for n in notify_bk20x_list:
                logger.debug(f"notify_bk20x_list list update: {n}")
                for u in notify_bk_dict[n]['uids']:
                    self.insert_user_notifications(u, f"New Case Activity", \
                    f"New Case Activity: {notify_bk_dict[n]['case_name']}", 'bk', n, None)#loss_id)

                if notify_bk_dict[n]['list_create'] == True:
                    cl = {
                    "name": f"BKWire Alert Creditors {n}",
                    "description": f"List of Customers following {notify_bk_dict[n]['case_name']}"
                    }
                    crl_resp = cc.create_lists(cl)
                    add_member = {
                    "source": {
                        "contact_ids":
                            notify_bk_dict[n]['ulist']
                    },
                    "list_ids": [
                        crl_resp['list_id']
                    ]
                    }
                    notify_bk_dict[n]['list_create'] = crl_resp['list_id']
                    logger.debug(cc.add_list_memberships(add_member))
                else:
                    # Compare user_ids in list to that of notifications
                    # Remove those not found in comp list
                    # ID over to remove function
                    add_member = {
                    "source": {
                        "contact_ids":
                            notify_bk_dict[n]['ulist']
                    },
                    "list_ids": [
                        notify_bk_dict[n]['list_create']
                    ]
                    }
                    logger.debug(cc.add_list_memberships(add_member))
                
                camp_name = f"BKWire Alert Creditors - {notify_bk_dict[n]['case_name']} - {date_object[2]} {date_object[3]} - {suuid}"
                load_html_resp = self.load_html_results_bk(loss_mysql_results, 'bkw_bankruptcy_notification_creditors_v2', bk_case_name=notify_bk_dict[n]['case_name'], dci_id=n)
                # HTML content generated from templates
                #logger.debug(load_html_resp)

                create_mail = {
                    "name": camp_name,
                    "email_campaign_activities": [{
                            "format_type": 5,
                            "from_email": "emily.taylor@bkwire.com",
                            "from_name": "Emily Taylor",
                            "reply_to_email": "emily.taylor@bkwire.com",
                            "subject": f"BKWire Alert Creditors Notice - {notify_bk_dict[n]['case_name']}",
                            "html_content": load_html_resp,
                    }]
                }
                # create Campaign BKWire Alert - Slug
                if notify_bk_dict[n]['ulist'] == None:
                    return 'Nothing to send'
                else:
                    create_emails_resp = cc.create_emails(create_mail)
                if create_emails_resp == None:
                    return 'Nothing to send'
                else:
                    logger.debug(create_emails_resp['campaign_activities'][0]['campaign_activity_id'])
                    # update Camp with ListID
                    update_mail = {
                        "name": camp_name,
                        "contact_list_ids": [notify_bk_dict[n]['list_create']],
                        "current_status": "DRAFT",
                        "format_type": 5,
                        "from_email": "emily.taylor@bkwire.com",
                        "from_name": "Emily Taylor",
                        "reply_to_email": "emily.taylor@bkwire.com",
                        "subject": f"BKWire Alert Creditors Notice - {notify_bk_dict[n]['case_name']}",
                        "html_content": load_html_resp,
                    }
                    logger.debug(cc.update_emails(update_mail, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))
                    # send email to list
                    send_mail_now = {
                        "scheduled_date": "0"
                    }
                    logger.info(cc.send_emails(send_mail_now, create_emails_resp['campaign_activities'][0]['campaign_activity_id']))

    def insert_user_notifications(self, uid, title, body, type, bkid, actid=None):
        bk_file_loader = FileSystemLoader('templates/sql')
        bk_env = Environment(loader=bk_file_loader)
        bk_template = bk_env.get_template('mysql_notify_users_insert')
        bk_output_insert = bk_template.render(userid=uid, status='unread', title=title, \
        body=body, type=type, bkid=bkid, actid=actid)
        self.db1.sql_commit(bk_output_insert)

    def search(self, Tuple, field, n):
        for i in range(len(Tuple)):
            if Tuple[i][field] == n:
                return True
        return False

    def load_case_sql_results(self, dcid):
        file_loader = FileSystemLoader('templates/sql')
        env = Environment(loader=file_loader)
        template = env.get_template('mysql_comp_query_notification')
        output = template.render(dc_id=dcid)
        return(self.db1.fetch_no_cache(output))

    def load_loss_sql_results(self, cname):
        date_object = self.bkw_dt.get_daily_time_w_month_day()
        file_loader = FileSystemLoader('templates/sql')
        env = Environment(loader=file_loader)
        template = env.get_template('mysql_loss_query_notification_watchlist')
        output = template.render(sdf=date_object[1], edf=date_object[0], creditor_name=cname)
        return(self.db1.fetch_no_cache(output))

    def load_html_results_comp(self, cname, loss_results):
        file_loader = FileSystemLoader('templates/html')
        env = Environment(loader=file_loader)
        template = env.get_template('bkw_company_notification_v2')
        output = template.render(creditor_name=cname, loss_data=loss_results)
        return(output)

    def load_html_results_bk(self, case_details, template_name, user_data=None, comment=None, bk_case_name=None, dci_id=None):
        file_loader = FileSystemLoader('templates/html')
        env = Environment(loader=file_loader)
        template = env.get_template(template_name)
        output = template.render(bk_data=case_details, user_comment=comment, user_data=user_data, bk_case_name=bk_case_name, dci_id=dci_id)
        return(output)
    
    def load_html_template(self, **kwargs):
        file_loader = FileSystemLoader('templates/html')
        env = Environment(loader=file_loader)
        template = env.get_template(kwargs['template_name'])
        output = template.render(kwargs=kwargs)
        return(output)    

def main():
    cn = CaseNotify()
    cn.build_bk_topic()
    #notify_bk20x_list = [4009]
    #notify_bk_dict = {4009: {'elist': ['cbford@1337itsolutions.com'], 'uids': [245], 'case_name': 'Dexter Group Investments, Inc.'}}
    #loss_mysql_results = [{'id': 85395, 'creditor_name': 'Alicia Kilburn', 'state_code': 'FL', 'city': 'Melbourne', 'industry': None, 'unsecured_claim': '$1,287,042', 'date_filed': '11-18', 'case_name': 'Dexter Group Investments, Inc.', 'dci_id': 4009}, {'id': 85396, 'creditor_name': 'Brevard County Tax Collector', 'state_code': 'FL', 'city': 'Titusville', 'industry': 'Business Services', 'unsecured_claim': '$51,047', 'date_filed': '11-18', 'case_name': 'Dexter Group Investments, Inc.', 'dci_id': 4009}, {'id': 85398, 'creditor_name': 'Pejman Jamshiddanaee', 'state_code': None, 'city': None, 'industry': None, 'unsecured_claim': '$502,000', 'date_filed': '11-18', 'case_name': 'Dexter Group Investments, Inc.', 'dci_id': 4009}]
    #cn.notify_bk_topic_creditors(notify_bk20x_list=notify_bk20x_list, notify_bk_dict=notify_bk_dict, loss_mysql_results=loss_mysql_results)

# MAIN
if __name__ == '__main__':
    main()
