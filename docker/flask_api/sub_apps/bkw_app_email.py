import re
import os, sys
import json
import time
import shortuuid
import logging.config
from logtail import LogtailHandler

## IMPORT CUSTOM MODULES ##
sys.path.insert(0, '/app')
from sub_apps.bkw_notifications_v2 import CaseNotify
from sub_apps import bkw_app_api_config
from modules.notifications.bkw_constantcontact import ConstantContact

### LOGGING SETUP ###
handler = LogtailHandler(source_token=os.environ['LOG_SOURCE_TOKEN'])
logger = logging.getLogger(__name__)
logger.handlers = []
logger.setLevel(logging.DEBUG) # Set minimal log level
logger.addHandler(handler) # asign handler to logger


class BkAppEmailFunctions:
    # Init the class
    def __init__(self):

        self.cn = CaseNotify()
        self.cc = ConstantContact()
    # Create company list
    # Update Member Info / Additional Custom Fields for Interested Zones(not just their industry zone)
    # Add members and tag if leader/member (based on email address domain/add team member func)
    # Generate the Email to team Leader
    # Generate the Email to team Member
    # Build email from passed args
    def build_campaign_email(self, **kwargs):
        """
        Build the necessary email components
        to start an Email Campaign in Constant Contact

        :param subject_line: string: Email Subject line to use for campaign email
        :param campaign_name: string: Campaign Name to use for campaign email - *This must be unique*
        :param email_address: list: User email address to create/update/add to list
        :param list_name: string: Campaign email list to which we add the user(create the list if doesn't already exist)
        :param html_temp_name: string: HTML template name to load for email body
        :return: 200/500 - based on outcome of this function
        """
        logger.info(f"Build Email Triggered: {kwargs}")

        msg = None
        cc_list = []
        cc_user_ids = []
        cc_list_id = None        
        list_create = True
        suuid = shortuuid.uuid()
        for k in kwargs['email_address']:
            # Create the contact details(cd) dictionary
            cd = {
                    "email_address": k,
                    "create_source": "Contact",
                    "list_memberships": [
                        "d13d60d0-f256-11e8-b47d-fa163e56c9b0" #required value
                    ]
            }
            # Pass to CC module for creation(will return ID if user already exists)
            cresp = self.cc.create_contact(cd)
            if cresp:
                logger.debug(f"create_contact successful: {cresp}")
                cc_user_ids.append(cresp['contact_id'])
            else:
                logger.error(f"create_contact failed: email NOT sent: {cd}")
                return msg

        # Get contact lists from CC
        cc_list = self.cc.get_lists()
        if cc_list:
            # Check if list exists and set ID or pass
            for c in cc_list['lists']:
                # if already exists, get list ID
                if c['name'] == kwargs['list_name']:
                    list_create = c['list_id']
        else:
            logger.error(f"get_lists failed: email NOT sent")
            return msg            

        logger.debug(f"list_create_ids: {list_create}")

        # IF true, setup contact list creation dictionary
        if list_create == True:
            logger.debug(f"list_create = True")
            cl = {
                    "name": kwargs['list_name'],
                    "description": f"BKW - {kwargs['list_name']}"
            }
            # Execute the CC create list module(passing cl data)
            crl_resp = self.cc.create_lists(cl)
            # Build add member dictionary for add_list_membership
            if crl_resp:
                logger.debug(f"create list: Success")
                add_member = {
                        "source": {
                        "contact_ids":
                            cc_user_ids
                        },
                        "list_ids": [
                            crl_resp['list_id']
                        ]
                }
            else:
                logger.error(f"create_lists failed: email NOT sent")
                return msg

            cc_list_id = crl_resp['list_id']
            logger.debug(f"add-member-dict: {add_member}")
            # Add member to list using data above
            alm = self.cc.add_list_memberships(add_member)
        else:
            logger.debug(f"list_create = False")
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
            logger.debug(f"add-member to existing list: {add_member}")
            # Add member to list using data above
            alm = self.cc.add_list_memberships(add_member)

        if alm:
            # Setup the Email Campaign Details
            camp_name = kwargs['camp_name']
            sub_line = kwargs['sub_line']
            from_name = bkw_app_api_config.constant_contact_from_name
            from_email = bkw_app_api_config.constant_contact_from_email_address
            html_output = self.cn.load_html_template(template_name=kwargs['html_temp_name'])

            # Setup the create_mail dictionary for email campaign
            create_mail = {
                "name": camp_name,
                "email_campaign_activities": [{
                        "format_type": 5,
                        "from_email": from_email,
                        "from_name": from_name,
                        "reply_to_email": from_email,
                        "subject": sub_line,
                        "html_content": html_output,
                }]
            }

            create_emails_resp = self.cc.create_emails(create_mail)
        else:
            logger.error(f"add_list_membership failed: email NOT sent")
            return msg            

        if create_emails_resp:
            logger.debug(f"Camp activity ID: {create_emails_resp['campaign_activities'][0]['campaign_activity_id']}")
            # update Camp with ListID
            update_mail = {
                "name": camp_name,
                "contact_list_ids": [cc_list_id],
                "current_status": "DRAFT",
                "format_type": 5,
                "from_email": from_email,
                "from_name": from_name,
                "reply_to_email": from_email,
                "subject": sub_line,
                "html_content": html_output,
            }
            cc_update_emails_resp = self.cc.update_emails(update_mail, create_emails_resp['campaign_activities'][0]['campaign_activity_id'])
            if cc_update_emails_resp:
                logger.debug(f"update_emails: Success")
            # send email to list
                send_mail_now = {
                    "scheduled_date": "0"
                }
            else:
                logger.debug(f"update_emails: Failed")
                msg = '500'

            cc_send_emails_resp = self.cc.send_emails(send_mail_now, create_emails_resp['campaign_activities'][0]['campaign_activity_id'])
            if cc_send_emails_resp:
                msg = '200'
            else:
                msg = '500'
        else:
            logger.error(f"create_emails_resp: Failed")
            msg = '500'
        
        return msg
    
# MAIN
if __name__ == '__main__':
    main()