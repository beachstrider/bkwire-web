import os,sys
import requests
import logging.config
from logtail import LogtailHandler
from os import path
## IMPORT CUSTOM MODULES ##
sys.path.insert(0, '/app')
from modules.database.db_select import dbSelectItems


## Set up logging
handler = LogtailHandler(source_token=os.environ['LOG_SOURCE_TOKEN'])
#log_file_path = path.join(path.dirname(path.abspath(__file__)), '/app/logging/logging.ini')
#logging.config.fileConfig(log_file_path)
#logger = logging.getLogger(__name__)
#logger_list = ['boto', 'boto3', 'chardet', 'urllib3', 'botocore', 's3transfer', 'PIL']
#for i in logger_list:
#    logging.getLogger(i).setLevel(logging.CRITICAL) #sets all #logging sources to crit level
# Create logger
logger = logging.getLogger(__name__)
logger.handlers = []
logger.setLevel(logging.DEBUG) # Set minimal log level
logger.addHandler(handler) # asign handler to logger

class CCTokenRefresh:
    def __init__(self):
        self.db1 = dbSelectItems()
        self.db1.db_login()
        self.rsession = requests.Session()

        base_api_url = 'https://api.cc.email/v3'
        self.update_email_url = f'{base_api_url}/emails/activities'
        self.emails_url = f'{base_api_url}/emails'
        self.get_contacts_url = f'{base_api_url}/contacts'
        self.create_list_url = f'{base_api_url}/contact_lists'
        self.signup_form = f'{base_api_url}/contacts/sign_up_form'
        self.get_list_url = f'{base_api_url}/contact_lists?include_count=false'
        self.add_list_member_url = f'{base_api_url}/activities/add_list_memberships'
        self.refresh_url = 'https://authz.constantcontact.com/oauth2/default/v1/token?refresh_token='
        self.sql_results_cc = self.db1.fetch_no_cache("SELECT * FROM constant_contact")


    def token_refresh(self):
        payload = None
        header_params = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': f"Basic {self.sql_results_cc[0]['client_secret']}"}
        refresh_url = f"{self.refresh_url}{self.sql_results_cc[0]['refresh_token']}&grant_type=refresh_token"

        try:
            search_req = self.rsession.post(refresh_url, headers=header_params, allow_redirects=True)
            if search_req.status_code == 200 or search_req.status_code == 201:
                logger.debug(f"Token Refresh Succeeded")
                payload = search_req.json()
            else:
                logger.error(f"Token Refresh returned non 2xx: {search_req.status_code}")
                exit(1)
        except Exception as e:
            logger.error(f"Token Refresh Failed: {e}")
            exit(1)
        else:
            return payload

    def update_token_refresh(self, data):
        logger.debug(data)
        sql = f"UPDATE `constant_contact` SET `access_token` = '{data['access_token']}', `refresh_token` = '{data['refresh_token']}' WHERE `constant_contact`.`id` = 1;"
        self.db1.sql_commit(sql)
        self.sql_results_cc = self.db1.fetch_no_cache("SELECT * FROM constant_contact")
        print(f"mysql token refresh success")

def main():
    cc = CCTokenRefresh()
    ccl = cc.token_refresh()
    if ccl != None:
        cc.update_token_refresh(ccl)
    else:
        logger.error(f"CC Token Refresh Failed")
        exit(1)
# MAIN
if __name__ == '__main__':
    main()
