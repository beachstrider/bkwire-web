import re
import os
import sys
import requests
import logging.config
from logtail import LogtailHandler
from os import path
sys.path.insert(0, '/app')
from modules.database.db_select import dbSelectItems

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

class ConstantContact:
    def __init__(self):
        self.db1 = dbSelectItems()
        self.db1.db_login()
        self.rsession = requests.Session()

        base_api_url = 'https://api.cc.email/v3'#https://api.cc.email/v3/emails/activities/dc7958d0-fdc2-4ecc-bd42-cf734664d72c?include=html_content
        self.update_email_url = f'{base_api_url}/emails/activities'
        self.emails_url = f'{base_api_url}/emails'
        self.get_contacts_url = f'{base_api_url}/contacts'
        self.create_list_url = f'{base_api_url}/contact_lists'
        self.signup_form = f'{base_api_url}/contacts/sign_up_form'
        self.get_list_url = f'{base_api_url}/contact_lists?include_count=false'
        self.add_list_member_url = f'{base_api_url}/activities/add_list_memberships'
        self.del_list_member_url = f'{base_api_url}/activities/remove_list_memberships'
        self.refresh_url = 'https://authz.constantcontact.com/oauth2/default/v1/token?refresh_token='
        self.sql_results_cc = self.db1.fetch_no_cache("SELECT * FROM constant_contact")

    def create_contact(self, contact_details):
        logger.debug(f"create_contact triggered: {contact_details}")
        # Create Contact
        data = contact_details
        create_contact = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}

        try:
            search_req = self.rsession.post(self.signup_form, headers=header_params, json=data, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Create/Update Contact Succeeded")
                create_contact = search_req.json()
            else:
                logger.warning(f"Create Contact/Update returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Create/Update Contact Failed: {e}")
        finally:
            return create_contact

    def get_lists(self):
        # Create Contact
        get_list = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}

        try:
            search_req = self.rsession.get(self.get_list_url, headers=header_params, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Get List Succeeded")
                get_list = search_req.json()
            else:
                logger.warning(f"Get List returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Get List Failed: {e}")
        finally:
            return get_list

    def get_list_details(self, listid):
        # Create Contact
        get_list = None
        get_list_details = f"{self.get_contacts_url}?lists={listid}"
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}

        try:
            search_req = self.rsession.get(get_list_details, headers=header_params, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Get List Succeeded")
                get_list_details = search_req.json()
            else:
                logger.warning(f"Get List returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Get List Failed: {e}")
        else:
            return get_list_details            

    def create_lists(self, list_details):
        # Create Contact
        data = list_details
        create_list_status = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}

        try:
            search_req = self.rsession.post(self.create_list_url, headers=header_params, json=data, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Create List Succeeded")
                create_list_status = search_req.json()
            else:
                logger.warning(f"Create List returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Create Contact Failed: {e}")
        finally:
            return create_list_status

    def add_list_memberships(self, members_add):
        logger.debug(f"add_list_memberships triggered")
        # Create Contact
        data = members_add
        add_member_status = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}
        #Get list details
        ccl = self.get_list_details(members_add['list_ids'][0])
        my_existing_user_list_ids = []
        for c in ccl['contacts']:
          my_existing_user_list_ids.append(c['contact_id'])
        #Delete any existing contacts
        del_member = {
                "source": {
            "contact_ids":
                  my_existing_user_list_ids
                },
                "list_ids": [
                  members_add['list_ids'][0]
                ]
        }
        if len(my_existing_user_list_ids) > 0:
          self.del_list_memberships(del_member)
        #Add new members to list - allows us to roll off those that no longer subscribe 
        try:
            search_req = self.rsession.post(self.add_list_member_url, headers=header_params, json=data, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"List Update Succeeded")
                add_member_status = search_req.json()
            else:
                logger.warning(f"List Update returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"List Update Failed: {e}")
        finally:
            return add_member_status

    def del_list_memberships(self, members_add):
        # Create Contact
        data = members_add
        add_member_status = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}

        try:
            search_req = self.rsession.post(self.del_list_member_url, headers=header_params, json=data, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"List User Delete Succeeded")
                add_member_status = search_req.json()
            else:
                logger.warning(f"List User Delete returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"List User Delete Failed: {e}")
        else:
            return add_member_status            

    def get_users(self, user_email=None):
        # Create Contact
        get_users = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}

        try:
            search_req = self.rsession.get(self.get_contacts_url, headers=header_params, params=user_email ,allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Get Users Succeeded")
                get_users = search_req.json()
            else:
                logger.warning(f"Get Users returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Create Contact Failed: {e}")
        else:
            return get_users

    def get_emails(self):
        # Create Contact
        get_emails = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}

        try:
            search_req = self.rsession.get(self.emails_url, headers=header_params, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Get Emails Succeeded")
                get_emails = search_req.json()
            else:
                logger.warning(f"Get Emails returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Get Emails Failed: {e}")
        else:
            return get_emails

    def create_emails(self, payload):
        logger.debug(f"create_emails triggered: {payload}")
        # Create Contact
        create_emails = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}

        try:
            search_req = self.rsession.post(self.emails_url, headers=header_params, json=payload, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Create Emails Succeeded")
                create_emails = search_req.json()
            else:
                logger.warning(f"Create Emails returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Create Emails Failed: {e}")
        finally:
            return create_emails

    def update_emails(self, payload, activity_id):
        update_emails = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}
        update_email_url = f"{self.update_email_url}/{activity_id}"
        try:
            search_req = self.rsession.put(update_email_url, headers=header_params, json=payload, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Update Emails Succeeded")
                update_emails = search_req.json()
            else:
                logger.warning(f"Update Emails returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Update Emails Failed: {e}")
        else:
            return update_emails

    def send_emails(self, payload, activity_id):
        send_emails = None
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}
        send_email_url = f"{self.update_email_url}/{activity_id}/schedules"
        try:
            search_req = self.rsession.post(send_email_url, headers=header_params, json=payload, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Send Emails Succeeded")
                send_emails = search_req.json()
            else:
                logger.warning(f"Send Emails returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Send Emails Failed: {e}")
        else:
            return send_emails

    def get_html_data_tables(self, activity_id):
        # Get Draft Camp
        json_w_html = None
        update_email_url = f"{self.update_email_url}/{activity_id}"
        header_params = {'content-type': 'application/json', 'Authorization': f"Bearer {self.sql_results_cc[0]['access_token']}"}
        url_filter = 'include=html_content'
        try:
            search_req = self.rsession.get(update_email_url, headers=header_params, params=url_filter ,allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Get Camps Succeeded")
                json_w_html = search_req.json()
            else:
                logger.warning(f"Get Camps returned non 2xx: {search_req.text}")
        except Exception as e:
            logger.error(f"Get Camps Failed: {e}")
        else:
            return(json_w_html)

def main():
    cc = ConstantContact()
    ccl = cc.get_list_details('d73b88a4-3ff0-11ed-b8f8-fa163e7b09ec')
    print(ccl)
    my_existing_user_list_ids = []
    for c in ccl['contacts']:
      print(c['contact_id'])
      my_existing_user_list_ids.append(c['contact_id'])

    add_member = {
            "source": {
        "contact_ids": [
            'a234ab30-0301-11ed-ac92-fa163e3c5d75'
          ]
            },
            "list_ids": [
            'd73b88a4-3ff0-11ed-b8f8-fa163e7b09ec'
            ]
    }
    del_member = {
            "source": {
        "contact_ids":
            my_existing_user_list_ids
            },
            "list_ids": [
            'd73b88a4-3ff0-11ed-b8f8-fa163e7b09ec'
            ]
    }
    #cc.del_list_memberships(del_member) 
    #cc_list_id = crl_resp['list_id']
    #print(f"add-member: {add_member}")
    #print(cc.add_list_memberships(add_member))    
    ghdt_response = cc.get_html_data_tables('63b41c17-e821-4e12-bdf3-05530676d919')
    file2 = open("MyFile2.html", "w")
    file2.writelines(str(ghdt_response['html_content']))
    file2.close()





# MAIN
if __name__ == '__main__':
    main()
