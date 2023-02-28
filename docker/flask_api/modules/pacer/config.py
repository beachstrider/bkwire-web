import os

s3_bkw_pacer_batch_reports = 'bkw.pacer-batch-reports'
pacer_username = os.environ['PACER_USERNAME']
pacer_password = os.environ['PACER_PASSWORD']
pacer_clientcode = os.environ['PACER_CLIENTCODE']
pacer_cso_login_url = os.environ['PACER_CSO_LOGIN_URL']
pacer_api_url = os.environ['PACER_API_URL']

pacer_client_code = '6430212'
chrome_hub = 'http://hub:4444/wd/hub'

case_data_filename = 'case_data.json'
case_data_full_path = f'/app/data/{case_data_filename}'

pacer_login_url = 'https://pacer.login.uscourts.gov/csologin/login.jsf?appurl=https://pcl.uscourts.gov/pcl/loginCompletion'
pacer_welcome_url = 'https://pcl.uscourts.gov/pcl/pages/welcome.jsf'
#https://pacer.login.uscourts.gov/csologin/login.jsf?appurl=https://pcl.uscourts.gov/pcl/loginCompletion
reg_find_list_end = [
    'inc\.',
    'corp\.', 
    'llc\.', 
    'l\.l\.c\.', 
    'co\.', 
    'ltd\.', 
    'pllc\.',
    'plc\.',
    'lp\.', 
    'l\.p\.'
]
reg_find_list_end_no_space = ['inc\.', 'corp\.', 'llc\.', 'l\.l\.c\.', 'ltd\.', 'pllc\.']
reg_find_list_any = [
    'american',
    'associates',
    'association',
    'baptist',
    'burger',
    'commercial',
    'community',
    'company',
    'construction',
    'corporation',
    'd/b/a',
    'dba',
    'enterprise',
    'environment',
    'equipment',
    'express',
    'financial',
    'foundation',
    'funds',
    'group',
    'holdings',
    'imports',
    'incorporado',
    'incorporated',
    'industrial',
    'industries',
    'investment',
    'lending',
    'limited',
    'logistics',
    'non-profit',
    'nonprofit',
    'office',
    'organization',
    'partnership',
    'parts',
    'products',
    'properties',
    'realty',
    'restaurant',
    'school',
    'services',
    'solutions',
    'system',
    'trust',
    'u\.s\.a\.'
]