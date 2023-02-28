import os

### bkw_app_api_funcs ###
user_values_add_cc = [
    'first_name',
    'last_name',
    'phone_number',
    'company_name',
    'company_sector'
]

trial_days = 14
team_level = 2
default_max_team_count = 2

mvp_price_monthly = os.environ['STRIPE_MVP_PRICE_ID']
mvp_price_yearly = os.environ['STRIPE_MVP_PRICE_ID_YEARLY']
team_stripe_price_monthly = os.environ['STRIPE_PRO_PRICE_ID']
team_stripe_price_yearly = os.environ['STRIPE_PRO_PRICE_ID_YEARLY']
individual_stripe_price_monthly = os.environ['STRIPE_BASIC_PRICE_ID']
individual_stripe_price_yearly = os.environ['STRIPE_BASIC_PRICE_ID_YEARLY']

mvp_stripe_price = [mvp_price_monthly, mvp_price_yearly]
team_stripe_price = [team_stripe_price_monthly, team_stripe_price_yearly]
individual_stripe_price = [individual_stripe_price_monthly, individual_stripe_price_yearly]

### bkw_app_email.py ###
constant_contact_from_name = 'Emily Taylor'
constant_contact_from_email_address = 'emily.taylor@bkwire.com'
