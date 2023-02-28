import re, sys
import json
import time
import logging.config

## IMPORT CUSTOM MODULES ##
sys.path.insert(0, '/app')
from sub_apps.bkw_app_email import BkAppEmailFunctions

BKAEF = BkAppEmailFunctions()
BKAEF.build_campaign_email(sub_line='Blake Test Team Leader',
                           camp_name='Blake Test Camp Team Leader3',
                           email_address='cbford03@gmail.com',
                           list_name='Blakes Rad Company Test Team Leader',
                           html_temp_name='bkw_team_leader')