# -*- coding: latin-1 -*-
import os
import json
import threading
import apminsight
from logtail import LogtailHandler
from os import path
from jose import jwt
import logging.config
from datetime import timedelta
from flask import Flask, jsonify, request, _request_ctx_stack, session
from flask_session import Session
from flasgger import Swagger, swag_from
from flask_cors import CORS, cross_origin
from six.moves.urllib.request import urlopen
from functools import wraps
## IMPORT CUSTOM MODULES ##
from modules.news import INDUSTRY_SCRAPER_MAPPING
from modules.stripe.bkw_stripe import StripeIntegrate
from modules.bkwdatetime.date_time import BkwDateTime
import sub_apps.bkw_app_api_funcs as pysearch 

## Set up logging
handler = LogtailHandler(source_token=os.environ['LOG_SOURCE_TOKEN'])
logger = logging.getLogger(__name__)
logger.handlers = []
logger.setLevel(logging.DEBUG) # Set minimal log level
logger.addHandler(handler) # asign handler to logger

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'BKWire API',
    'uiversion': 3,
    'openapi': '3.0.2',
    'version': '2.0.1'
}
app.config['SESSSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = "filesystem"
app.config['SESSION_FILE_THRESHOLD'] = 500
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SECRET_KEY'] = 'myrandomstringhere'
swagger_template = {
    'components': {
        'securitySchemes': {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT'
            }
        },
        'security': {
            'bearerAuth': []
        }
    }
}

sess = Session(app)
CORS(app)

swagger = Swagger(app, template=swagger_template)
application = app
AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
API_AUDIENCE = os.environ['AUTH0_AUDIENCE']
ALGORITHMS = ["RS256"]

# Error handler #
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

# Format error response and append status code
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token

def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/",
                    options={"verify_signature": False}
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            us = UserSession(payload)
            us.check_user()            
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated

# Error handler
class UserSession:
    def __init__(self, payload):
        self.payload = payload

    def check_user(self):
        try:
            if self.payload['https://bkwire.com/email']:
                if 'user_id' in session and 'customer_id' in session:
                    logger.debug('User session has been established!')
                    return
                else:
                    #check the database for existence
                    user_id_from_db = pysearch.get_user_id(user_email=self.payload['https://bkwire.com/email'])
                    print(f"user_id_from_db: {user_id_from_db}")
                    if len(user_id_from_db[0]) > 0:
                        session['user_id'] = user_id_from_db[0][0]['id']
                        user_elements_from_db = pysearch.get_user(session['user_id'])
                        #Update user in DB with Auth0 ID / is_social
                        is_social = self.payload['https://bkwire.com/is_social']
                        if is_social != user_elements_from_db[0][0]['is_social']:
                            pysearch.update_user(session['user_id'], is_social=str(is_social).lower())
                        if user_elements_from_db[0][0]['auth0'] != self.payload['https://bkwire.com/user_id']:
                            pysearch.update_user(session['user_id'], auth0=self.payload['https://bkwire.com/user_id'])
                        #create stripe customer if this user doesn't have one
                        if user_elements_from_db[0][0]['customer_id']:
                            session['customer_id'] = user_elements_from_db[0][0]['customer_id']
                    else:
                        first_name = None
                        last_name = None
                        try:
                            first_name = self.payload['https://bkwire.com/given_name']
                            last_name = self.payload['https://bkwire.com/family_name']
                        except:
                            logger.warning('No Given + Family name found')
                        try:
                            first_name, last_name = self.payload['https://bkwire.com/name'].split()
                        except:
                            logger.warning('No name found, creating with email')
                        finally:
                            nuid = pysearch.create_user(first_name=first_name, last_name=last_name, email_address=self.payload['https://bkwire.com/email'], phone_number=None, company_name=None, company_state=None, company_zip_code=None, email_alerts_enabled=True, email_alert_1=None, email_alert_2=None, email_alert_3=None, text_alerts_enabled=False, phone_alert_1=None, phone_alert_2=None, phone_alert_3=None, is_social=self.payload['https://bkwire.com/is_social'], auth0=self.payload['https://bkwire.com/user_id'], company_sector=None)
                            session['user_id'] = nuid[1]
            return
        except Exception as e:
            logger.error(f'Failed to parse indentifying information from JWT payload: {e}')
            session['user_id'] = None
            session['customer_id'] = None

"""API ROUTES DEFINED BELOW - all functions are calls to sub_apps.bkw_app_api_funcs"""
@app.route('/change-password', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/change-password.yml')
@requires_auth
def change_pass():
    user_elements_from_db = pysearch.get_user(session['user_id'])
    return(pysearch.change_password(user_elements_from_db[0][0]['auth0'], **request.form.to_dict()))

@app.route('/search')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/header-search.yml')
@requires_auth
def search():
    return(jsonify(pysearch.header_search(**request.args.to_dict(flat=False))[0]))

@app.route('/industries')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/industries.yml')
@requires_auth
def industries():
    return(jsonify(pysearch.industries()[0]))

@app.route('/bk-graph')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/home-graph.yml')
@requires_auth
def bk_graph():
    return(jsonify(pysearch.bk_graph()))

@app.route('/list-bankruptcies')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/list-bks.yml')
@requires_auth
def list_bks():
    return(jsonify(pysearch.list_bankruptcies(session['user_id'], **request.args.to_dict(flat=False))[0]))

@app.route('/list-losses')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/list-losses.yml')
@requires_auth
def list_losses():
    return(jsonify(pysearch.list_losses(session['user_id'], **request.args.to_dict(flat=False))[0]))

@app.route('/create-team-user', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/create-team-user.yml')
@requires_auth
def create_team_user():
    return(pysearch.create_team_user(userid=session['user_id'], **request.json))

@app.route('/delete-team-user', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/delete-team-user.yml')
@requires_auth
def delete_team_user():
    return(pysearch.delete_team_user(userid=session['user_id'], **request.json))

@app.route('/create-user', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/create-user.yml')
@requires_auth
def create_user():
    return(pysearch.create_user(**request.form.to_dict()))

@app.route('/update-user', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/update-user.yml')
@requires_auth
def update_user():
    return(pysearch.update_user(session['user_id'], **request.json))

@app.route('/update-user-industry', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/update-user-industries.yml')
@requires_auth
def update_user_industry():
    return(pysearch.update_user_industry(session['user_id'], **request.form.to_dict()))

@app.route('/get-user')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/get-user.yml')
@requires_auth
def get_user():
    return(jsonify(pysearch.get_user(session['user_id'])[0][0]))

@app.route('/get-user-file-access')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/get-user-file-access.yml')
@requires_auth
def get_user_file_access():
    return(jsonify(pysearch.get_user_file_access(session['user_id'], **request.args.to_dict(flat=False))))

@app.route('/pdf-form')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/pdf-form.yml')
@requires_auth
def view_pdf_form():
    return(jsonify(pysearch.view_pdf_form(**request.args.to_dict(flat=False))))

@app.route('/view-docket')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/view-docket.yml')
@requires_auth
def view_pacer_docket():
    return(jsonify(pysearch.view_pacer_docket(**request.args.to_dict(flat=False))))

@app.route('/view-bankruptcies')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/view-bks.yml')
@requires_auth
def view_bks():
    return(jsonify(pysearch.view_bankruptcies(session['user_id'], **request.args.to_dict(flat=False))[0]))

@app.route('/add-to-bk-watchlist', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/add-to-bk-watchlist.yml')
@requires_auth
def add_bks_watchl():
    return(pysearch.add_bk_watchlist(session['user_id'], **request.json))

@app.route('/remove-from-bk-watchlist', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/del-from-bk-watchlist.yml')
@requires_auth
def del_bks_watchl():
    return(pysearch.del_bk_watchlist(session['user_id'], **request.json))

@app.route('/list-bankruptcies-watchlist')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/list-bks-watchlist.yml')
@requires_auth
def list_bks_watchl():
    return(jsonify(pysearch.list_bankruptcies_watchlist(session['user_id'], **request.args.to_dict(flat=False))[0]))

@app.route('/add-to-companies-watchlist', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/add-to-comp-watchlist.yml')
@requires_auth
def add_comp_watchl():
    return(pysearch.add_comp_watchlist(session['user_id'], **request.json))

@app.route('/remove-from-companies-watchlist', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/del-from-comp-watchlist.yml')
@requires_auth
def del_comp_watchl():
    return(pysearch.del_comp_watchlist(session['user_id'], **request.json))

@app.route('/list-companies-watchlist')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/list-comp-watchlist.yml')
@requires_auth
def list_comp_watchl():
    return(jsonify(pysearch.list_comp_watchlist(session['user_id'], **request.args.to_dict(flat=False))[0]))

@app.route('/pacer-daily-import')
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def pacer_daily_import():
    return(jsonify(pysearch.list_comp_watchlist(session['user_id'], **request.args.to_dict(flat=False))[0]))

@app.route('/splash-losses')
@swag_from('templates/swagger/splash-screen-loss.yml')
def list_splash():
    return(jsonify(pysearch.list_splash()[0]))

@app.route('/list-cities')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/list-cities.yml')
@requires_auth
def list_cities():
    return(jsonify(pysearch.list_cities(**request.args.to_dict(flat=False))[0]))

@app.route('/list-notifications')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/list-notifications.yml')
@requires_auth
def list_notifications():
    return(jsonify(pysearch.list_notifications(session['user_id'], **request.args.to_dict(flat=False))[0]))

@app.route('/read-notification', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/read-notification.yml')
@requires_auth
def read_notification():
    return(pysearch.read_notification(**request.json))

@app.route('/read-notifications', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/read-notifications.yml')
@requires_auth
def read_notifications():
    return(pysearch.read_notifications(session['user_id'], **request.form.to_dict()))

@app.route('/delete-notifications', methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/delete-notifications.yml')
@requires_auth
def delete_notifications():
    return(pysearch.delete_notifications(session['user_id'], **request.form.to_dict()))
## hidden - no auth ##
@app.route('/daily-bk-report')
def daily_report():
    title = 'Daily BKWire Digest'
    schedule = 'daily'
    sub_line = 'Todays notable Corp BKs'
    return(pysearch.generate_bk_digest(schedule, title, sub_line))

@app.route('/weekly-bk-report')
def weekly_report():
    title = 'Weekly BKWire Digest'
    schedule = 'weekly'
    sub_line = 'This weeks notable Corp BKs'
    return(pysearch.generate_bk_digest(schedule, title, sub_line))

@app.route('/share-case')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/share-case.yml')
@requires_auth
def share_case():
    return(pysearch.share_case(session['user_id'], **request.args.to_dict(flat=False)))

@app.route('/share-loss')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/share-loss.yml')
@requires_auth
def share_loss():
    return(pysearch.share_loss(session['user_id'], **request.args.to_dict(flat=False)))

@app.route('/case-refresh')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/bk-case-refresh.yml')
@requires_auth
def case_refresh():
    # Thread this call as it could be long running
    t = threading.Thread(target=pysearch.case_refresh, args=[session['user_id']], kwargs=request.args.to_dict(flat=False))
    t.setDaemon(False)
    t.start()
    # Return result to FE as a notification will go to user upon completion
    return '200'

@app.route('/file-link-get')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/bk-file-link-get.yml')
@requires_auth
def file_link_get():
    return(jsonify(pysearch.file_link_get(session['user_id'], **request.args.to_dict(flat=False))))

@app.route('/file-link-download')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/bk-file-link-download.yml')
@requires_auth
def file_link_download():
    return(jsonify(pysearch.file_link_download(session['user_id'], **request.args.to_dict(flat=False))))    
##### STRIPE ######
@app.route('/manage')
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/manage-stripe.yml')
@requires_auth
def customer_portal():
    si = StripeIntegrate()
    return(si.customer_portal(**request.args.to_dict(flat=False)))


@app.route('/subscribe', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/subscribe-stripe.yml')
@requires_auth
def update_subscription():
    si = StripeIntegrate()
    user_data = pysearch.get_user(session['user_id'])[0][0]
    return(si.update_subscription(user_data, **request.args.to_dict(flat=False)))


@app.route('/webhook', methods=['POST'])
def webhook():
    si = StripeIntegrate()
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    return(si.webhook(payload, sig_header))

##### NEWS ######
@app.route("/bk-news")
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/bk-news.yml')
@requires_auth
def news():
    my_req_args = request.args.to_dict(flat=False)
    bkw_dt = BkwDateTime()
    date_object = bkw_dt.get_news_length()
    previous_news_date = date_object[1]
    try:
        industry_id = my_req_args['industry'][0]
        logger.debug(industry_id)
    except:
        industry_id = ""

    if industry_id == "":
        industry = "general"
    else:
        industry_name = pysearch.run_sql_queries_no_cache(f"SELECT naics_desc from industry_desc WHERE id='{industry_id}'")
        logger.debug(industry_name)
        industry = industry_name[0][0]['naics_desc'].lower()

    if industry in INDUSTRY_SCRAPER_MAPPING:
        #mysql_get_latest_news_query = f"SELECT * FROM (SELECT Title, Link, Snippet, date FROM news WHERE Industry = '{industry}' ORDER BY Id DESC LIMIT 10) AS freshnews ORDER BY date DESC;"
        mysql_get_latest_news_query = f"SELECT * FROM (SELECT Title, Link, Snippet, date FROM news WHERE Industry = '{industry}' AND date between '{previous_news_date}' and now() ORDER BY Id DESC LIMIT 10) AS freshnews ORDER BY date DESC;"
        industry_records = pysearch.run_sql_queries_no_cache(mysql_get_latest_news_query)
        latest_news_list = []
        for latest_record in industry_records[0]:
            news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
            news_dict["Title"] = latest_record['Title']
            news_dict["Link"] = latest_record['Link']
            news_dict["Snippet"] = latest_record['Snippet']
            news_dict["date"] = latest_record['date']
            latest_news_list.append(news_dict)
        return jsonify(latest_news_list)
    else:
        pass 

@app.route("/scrape/bk-news", methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@swag_from('templates/swagger/bk-scrape-news.yml')
def scrapenews():
    all_records = []
    result = None
    sql_commit_query = "CREATE TABLE if not exists news (Id INT PRIMARY KEY AUTO_INCREMENT, Title  VARCHAR(2000), Snippet VARCHAR(2000), Link VARCHAR(1000), Industry VARCHAR(30), date VARCHAR(20))"
    pysearch.run_sql_commit(sql_commit_query)
    for industry_name_key in INDUSTRY_SCRAPER_MAPPING:
        try:
            news_data = INDUSTRY_SCRAPER_MAPPING[industry_name_key]().get_news()
            logger.debug(news_data)
            for item in news_data:
                insert_record = ()
                insert_record = (
                    item.get("Title"),
                    item.get("Snippet"),
                    item.get("Link"),
                    industry_name_key,
                    item.get("date"),
                )
                all_records.append(insert_record)            
        except Exception as e:
            logger.error(f"News scrapper failed: {industry_name_key}: {e}")
            pass
    pysearch.run_sql_truncate('news')
    mysql_insert_query = "INSERT INTO news (Title, Snippet, Link, Industry, date) VALUES (%s, %s, %s, %s, %s)"
    try:
        result = pysearch.run_sql_commit_many(mysql_insert_query, all_records)
    except:
        logger.error(f"Scrape news commit - Failed")
    return result


if __name__ == "__main__":
    #app.run(debug=True)
    pass
