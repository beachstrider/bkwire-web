#!/usr/bin/python

import re
import os,sys
import datetime
import logging.config
from logtail import LogtailHandler
import mysql.connector
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from os import path

### MODULE SETUP ###
sys.path.insert(0, '/app')
from modules.database import config

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

### DATETIME SETUP ###
now  = datetime.datetime.now()
db_ts = now.strftime('%Y/%m/%d')
config_create_date = now.strftime('%Y%d%m%H%M%S')
xmlDict = {}

def lookup_naics_prefixes():
    cnxn = db_login()
    cursor = cnxn.cursor(dictionary=True)
    sql = """SELECT id,naics_codes FROM industry_desc WHERE 1"""
    cursor.execute(sql)
    data = cursor.fetchall()
    return(data)

def db_login():
    try:
        conn = mysql.connector.connect(
        user=config.user,
        password=config.password,
        host=config.host,
        database=config.database,
        auth_plugin='mysql_native_password')
    except Exception as e:
        logger.info('login failed! ')
        logger.error(e)
        return False
    return(conn)

#################### NEW 2.0 ############################
def check_if_company_exists(cnxn, comp_name):
    cursor = cnxn.cursor()
    sql = """SELECT name FROM companies WHERE slug = %s"""
    cursor.execute(sql, [comp_name])
    row = cursor.fetchone()
    if not row is None:
        try:
            logger.debug("company_name exists in db: " + str(comp_name))
            return(str(row[0]))
        except:
            logger.debug("Something went wrong with SELECT query: " + str(comp_name))
    else:
        logger.debug("company_name does NOT exist in company table: " + str(comp_name))
    return(False)

def check_if_company_info_exists(cnxn, comp_name):
    cursor = cnxn.cursor()
    comp_scrub = company_scrub(comp_name)
    company_slug = create_company_slug(comp_scrub)
    check_result_company = check_if_company_exists(cnxn, company_slug)
    if check_result_company is not False:
        comp_name = check_result_company
    else:
        comp_name = title(comp_name)
    try:
        sql = """SELECT id FROM company_information WHERE company_name = %s"""
        cursor.execute(sql, [comp_name])
        row = cursor.fetchone()

        if row is not None:
            try:
                logger.debug("id exists in company_info table: " + str(comp_name))
                return(str(row[0]))
            except:
                logger.debug("Something went wrong with SELECT query: " + str(comp_name))
        else:
            logger.debug("company_name does NOT exist in company info table: " + str(comp_name))        
    except Exception as e:
        logger.error(f"Company Info Check Failed")

    return(None)

def check_if_case_exists(cnxn, bfd_id):
    cursor = cnxn.cursor()
    sql = """SELECT id FROM bankruptcy_filing_data WHERE dci_id = %s"""
    cursor.execute(sql, [bfd_id])
    row = cursor.fetchone()
    if not row is None:
        try:
            logger.debug("bankruptcy filing id = " + str(row[0]))
            logger.debug("bankruptcy filing exists in db: " + str(bfd_id))
            return(str(row[0]))
        except:
            logger.debug("Unable to find db_id: " + str(bfd_id))
            return(None)
    else:
        logger.debug("bankruptcy filing does NOT exist: " + str(bfd_id))
        return(None)

def check_if_file_exists_inv(cnxn, file_name):
    cursor = cnxn.cursor(buffered=True)
    sql = """SELECT id FROM bkw_files WHERE name = %s"""
    cursor.execute(sql, [file_name])
    row = cursor.fetchone()
    if not row is None:
        try:
            logger.debug("bkw_files id = " + str(row[0]))
            logger.debug("bkw_files exists in db: " + str(file_name))
            return(str(row[0]))
        except:
            logger.debug("Unable to find db_id: " + str(file_name))
            return(None)
    else:
        logger.debug("bkw_files does NOT exist: " + str(file_name))
        return(None)        

def insert_companies(cnxn, company_name, ncode=511):
    #Debtor Company Information table
    cursor = cnxn.cursor()
    comp_scrub = company_scrub(company_name)
    case_title_comp = title(comp_scrub)
    company_slug = create_company_slug(comp_scrub)
    check_result_company = check_if_company_exists(cnxn, company_slug)
    ncode_id = look_naics_key(ncode)
    if check_result_company is False:
        try:
            sql = """INSERT INTO companies (name, slug, industry_id)
            VALUES (%s,%s,%s)"""
            val = (case_title_comp, company_slug, ncode_id)
            cursor.execute(sql, val)
            cnxn.commit()
            # Get ID of db entry for later use
            logger.debug('MySQL: companies commit successful!')
        except Exception as e:
            logger.warning('companies commit FAILED: ' + str(e))
            logger.debug(company_name)
            pass
    else:
        logger.debug('companies commit exists: ' + company_name)

def company_scrub(company_name):
    remove_float_numbers = []
    try:
        remove_float_numbers = re.findall("\d+\.\d+", company_name)
        if len(remove_float_numbers) > 0:
            for r in remove_float_numbers:
                company_name = company_name.replace(r, '')
        company_name = company_name.replace('basis for the claim:', '')
        company_name = company_name.replace('basis for the claim', '')
        company_name = company_name.replace('trade debt', '')
        company_name = company_name.replace('$', '')
        company_name = company_name.replace('Date S Debt Was Incurred', '')
        company_name = company_name.replace('Date or Dates Debt Was Incurred', '')
    except Exception as e:
        logger.error(f"Company scrub failed: {e}, {company_name}")
    return company_name

def title_word(chunk):
    """Title-case a given word (or do noting to a non-word chunk)."""

    DO_NOT_TITLE = [
        "a", "an", "and", "as", "at", "all", "but", "by", "en", "for", "from", "if",
        "in", "nor", "of", "on", "or", "per", "the", "to", "v", "vs", "via", "with"
        
    ]

    ALWAYS_TITLE = ["llc", "ltd", "pllc", "pc", "dds,"]

    try:
        if chunk.lower() in ALWAYS_TITLE:
            return chunk[0].upper() + chunk[1:].upper()
        if len(chunk) <= 2 and chunk.lower() not in DO_NOT_TITLE:
            return chunk[0].upper() + chunk[1:].upper()

        return chunk[0].upper() + chunk[1:].lower()
    except:
        logger.warning(f"Unable to handle word for title: {chunk}")
        return chunk

def title(value):
    strip_things = value.replace(',','').replace('.','')
    value = strip_things
    words_and_nonword_chunks = re.split(r"""
        (                   # capture both words and the chunks between words
            (?:             # split on consecutive:
                \s |        # - whitespace characters
                -  |        # - dashes
                "  |        # - double quotes
                [\[({<]     # - opening brackets and braces
            )+
        )
    """, value, flags=re.VERBOSE)
    return "".join(
        # upper/lower-casing symbols and whitespace does nothing
        title_word(chunk)
        for chunk in words_and_nonword_chunks
    )

def create_company_slug(company_name):
    try:
        company_name = company_name.replace(' ', '-').lower()
        company_name = re.sub(r'[^\w-]', '', company_name)
        slug_name = company_name.replace('--', '-')
        return(slug_name)
    except Exception as e:
        logger.warning(f"company slug failed: {e}")
        return company_name

def insert_data_dci(cnxn, pacer_data_results):
    #Debtor Company Information table
    cursor = cnxn.cursor()    
    for k in pacer_data_results:
        comp_scrub = company_scrub(k)
        company_slug = create_company_slug(comp_scrub)
        check_result_company = check_if_company_exists(cnxn, company_slug)
        if check_result_company is not None:
            company_name = check_result_company
        else:
            company_name = title(comp_scrub)
        check_result_company_info = check_if_company_info_exists(cnxn, company_name) 
        
        if check_result_company_info is None:
            try:
                if 'company_address' in pacer_data_results[k]:
                    if pacer_data_results[k]['company_address'] != None:
                        title_company_address = title(pacer_data_results[k]['company_address'])
                    else:
                        title_company_address =  pacer_data_results[k]['company_address']
                sql = """INSERT INTO company_information (company_name, company_address, company_zip)
                VALUES (%s,%s,%s)"""
                val = (company_name, title_company_address, pacer_data_results[k]['company_zip'])
                cursor.execute(sql, val)
                cnxn.commit()

                pacer_data_results[k]['dci_id'] = cursor.lastrowid
                logger.debug("1 record inserted, ID: " + str(cursor.lastrowid))
                logger.debug('MySQL: company_information commit successful!')
            except Exception as e:
                try:
                    if 'company_address' in pacer_data_results[k]:
                        if pacer_data_results[k]['company_address'] != None:
                            title_company_address = title(pacer_data_results[k]['company_address'])
                        else:
                            title_company_address =  pacer_data_results[k]['company_address']                    
                    sql = """INSERT INTO company_information (company_name, company_address, company_zip)
                    VALUES (%s,%s,%s)"""
                    val = (company_name, title_company_address, None)
                    cursor.execute(sql, val)
                    cnxn.commit()

                    pacer_data_results[k]['dci_id'] = cursor.lastrowid
                    logger.debug("1 record inserted, ID: " + str(cursor.lastrowid))
                    logger.warning(f'MySQL: company_information commit successful!: missing zip: {company_name}')
                except Exception as e:
                    logger.warning('company_information commit FAILED: ' + str(e))
                    logger.debug(k)
                    pass
        else:
            pacer_data_results[k]['dci_id'] = int(check_result_company_info)

def insert_docket_data(cnxn, pacer_data_results):
    #Docket Information Table
    cursor = cnxn.cursor()
    for k in pacer_data_results:
        check_result_case = None
        try:
            check_result_case = check_if_case_exists(cnxn, pacer_data_results[k]['dci_id'])
        except Exception as e:
            logger.error('check_if_case_exists ddata FAILED' + str(e))
            pass
        if check_result_case is not None and 'docket_table' in pacer_data_results[k]:
            if not pacer_data_results[k]['docket_table'] is None:
                for dt in pacer_data_results[k]['docket_table']:
                    try:
                        entry_date,doc_url,pages,docs,activity,extra_docs = dt.split(':bkwsplit:')
                        sql = """INSERT INTO docket_table (entry_date, pages, docs, doc_url, activity, case_id)
                        VALUES (%s,%s,%s,%s,%s,%s)"""
                        val = (entry_date, pages, docs, doc_url, activity.strip(), pacer_data_results[k]['dci_id'])
                        cursor.execute(sql, val)
                        cnxn.commit()

                        pacer_data_results[k]['docket_files_link_id'] = cursor.lastrowid
                    except Exception as e:
                        logger.warning(f"docket_table commit FAILED: {e} {k}")
                        logger.debug(pacer_data_results)
                        pass            
                logger.debug('MySQL: docket_table commit successful!')
            else:
                logger.debug('MSYQL: docket_table is None')
        else:
            logger.debug('existing case data does not exist: ' + str(check_result_case))

def insert_data_bfd(cnxn, pacer_data_results):
    #Debtor Company Information table
    cursor = cnxn.cursor()
    for k in pacer_data_results:
        check_result_case = None
        comp_scrub = company_scrub(k)
        company_slug = create_company_slug(comp_scrub)
        check_result_company = check_if_company_exists(cnxn, company_slug)
        if check_result_company is not None:
            company_name = check_result_company
        else:
            company_name = title(comp_scrub)        
        try:
            check_result_case = check_if_case_exists(cnxn, pacer_data_results[k]['dci_id'])
        except Exception as e:
            logger.error('check_if_case_exists bfd FAILED: ' + str(e))
            pass
        if check_result_case is None:
            try:
                sql = """INSERT INTO bankruptcy_filing_data (court_id, cs_number, cs_office, cs_chapter, \
                 date_filed, case_number, case_link, case_name, dci_id, status_201, status_204206, involuntary, sub_chapv)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                val = (pacer_data_results[k]['court_id'], pacer_data_results[k]['cs_number'], \
                pacer_data_results[k]['cs_office'], pacer_data_results[k]['cs_chapter'], \
                pacer_data_results[k]['date_filed'], pacer_data_results[k]['case_number'],\
                pacer_data_results[k]['case_link'], company_name, \
                pacer_data_results[k]['dci_id'], pacer_data_results[k]['parse_201_attempt'], \
                pacer_data_results[k]['parse_204206_attempt'], pacer_data_results[k]['involuntary'], pacer_data_results[k]['sub_chapv'])
                cursor.execute(sql, val)
                cnxn.commit()

                filing_id = cursor.lastrowid
                pacer_data_results[k]['bkw_filing_id'] = filing_id
                logger.debug('MySQL: bankruptcy_filing_data commit successful!')

            except Exception as e:
                logger.warning(f"bankruptcy_filing_data commit FAILED: {e} {k}")
                logger.debug(pacer_data_results)
                pass
        else:
            logger.debug('existing case data: ' + str(check_result_case))
            pacer_data_results[k]['bkw_filing_id'] = check_result_case

def update_data_bfd(cnxn, pacer_data_results):
    #Debtor Company Information table
    cursor = cnxn.cursor()
    for k in pacer_data_results:
        try:
            sql = """UPDATE bankruptcy_filing_data SET status_204206 = %s WHERE dci_id = %s"""
            val = (pacer_data_results[k]['parse_204206_attempt'], pacer_data_results[k]['dci_id'])
            cursor.execute(sql, val)
            cnxn.commit()
            logger.debug(f"bankruptcy_filing_data update successful")
        except Exception as e:
            logger.warning(f"bankruptcy_filing_data update FAILED: {e} {k}")
            pass

def doc_entry_file_link_table_id(cnxn, file_link, case_id):
    cursor = cnxn.cursor()
    logger.debug(f"doc_entry_file_link_table_id: {file_link}, {case_id}")
    sql = """SELECT id FROM docket_entry_file_links WHERE docket_entry_link = %s AND docket_case_id = %s"""
    cursor.execute(sql, [file_link, case_id])
    row = cursor.fetchone()
    if not row is None:#https://ecf.flmb.uscourts.gov/doc1/046085836126
        try:
            logger.debug("docket_entry_file_links_id exists in db: " + str(row[0]))
            return(row[0])
        except Exception as e:
            logger.warning(f"Unable to find docket_entry_file_links entry: {e}, {sql}")
            return(None)

def doc_table_get_id(cnxn, file_link, case_id):
    dupe_list = []
    cursor = cnxn.cursor()
    sql = """SELECT DISTINCT id, SUBSTRING_INDEX(activity, ' ',4) as act_result FROM docket_table WHERE doc_url = %s AND case_id = %s"""
    cursor.execute(sql, [file_link, case_id])
    row = cursor.fetchall()
    if not row is None:
        try:
            logger.debug(f"doc_table_get_id - docket_table id exists in db: {row}")
            if len(row) > 1:
                # remove one of the elements from the DB as it shouldn't be there
                logger.warning(f"Found multiple doc_table_get_id: {file_link}, {case_id} - removing entry!")
                for r in row:
                    dupe_list.append(r)
                    dupe_list.sort()
                data = dupe_list.pop()
            else:
                data = row
        except Exception as e:
            logger.error(f"Unable to find docket_entry_file_links entry: {e}, {sql}")
            data = None
        finally:
            remove_old_docket_entry_if_exist(dupe_list)
            return data

def remove_old_docket_entry_if_exist(remove_dupe):
    cnxn = db_login()
    cursor = cnxn.cursor()
    logger.debug(f"remove_old_docket_entry_if_exist dupe list: {remove_dupe}")
    # we changed the length of activity and caused dupes on activity during a refresh
    # this should be temporarily needed as cases are cleanen up
    for r in remove_dupe:
        sql = """DELETE FROM docket_table WHERE id = %s"""
        cursor.execute(sql, [r[0]])
    cnxn.commit()
    cursor.close() 

def insert_files_inventory(pacer_data_results):
    logger.debug('insert_files_inventory triggered')
    cnxn = db_login()
    cursor = cnxn.cursor()
    for k in pacer_data_results:
        if 'pdf_doc_files' in pacer_data_results[k]:
            logger.debug('insert_files_inventory: pdf_doc_files exists')
            if len(pacer_data_results[k]['pdf_doc_files']) > 0:
                for p in pacer_data_results[k]['pdf_doc_files']:
                    pacer_data_results[k][p['filename']] = {}
                    response = check_if_file_exists_inv(cnxn, p['filename'])
                    if response is None:
                        try:
                            docket_file_link_id = doc_entry_file_link_table_id(cnxn, p['link'], pacer_data_results[k]['dci_id'])
                            logger.debug(f"docket_file_link_id: {docket_file_link_id}")
                            sql = """INSERT INTO bkw_files (name, file_type, bfd_id, de_file_links_id)
                            VALUES (%s, %s, %s, %s)"""
                            val = (p['filename'], p['type'], pacer_data_results[k]['bkw_filing_id'], int(docket_file_link_id))
                            cursor.execute(sql, val)
                            cnxn.commit()
                            logger.debug('MySQL: insert_files_inventory commit successful!')
                            pacer_data_results[k][p['filename']]['bkw_files_id'] = cursor.lastrowid
                        except Exception as e:
                            logger.error(f"insert_files_inventory commit FAILED: {e}: {k}")
                    else:
                        pacer_data_results[k][p['filename']]['bkw_files_id'] = response
            else:
                pass
        else:
            logger.debug('insert_files_inventory: pdf_doc_files NOT found')
            pass
    cursor.close()        

def insert_purchases(cnxn, guid, pacer_data_results):
    cursor = cnxn.cursor()
    logger.debug(f"insert_files_purchases triggered")    
    for k in pacer_data_results:
        try:
            for p in pacer_data_results[k]['pdf_doc_files']:
                sql = """INSERT INTO purchases (idpurchases, user_id)
                VALUES (%s, %s)"""
                val = (pacer_data_results[k][p['filename']]['bkw_files_id'], guid)
                cursor.execute(sql, val)
                cnxn.commit()
                logger.debug('MySQL: insert_purchases commit successful!')
        except Exception as e:
            logger.warning(f"insert_purchases commit FAILED: {e}: {k}")
            pass

def insert_docket_entry_file(cnxn, dkt_e_id=None, dkt_e_name=None, dkt_e_link=None, dkt_case_id=None, pdr=None):
    logger.debug(f"insert_docket_entry_file triggered")
    logger.debug(f"tshoot these ARGS: {dkt_e_id}, {dkt_e_name}, {dkt_e_link}, {dkt_case_id}, {pdr}")
    #[(126644, 'CORPORATE RESOLUTION. Filed by')], Main Document, https://ecf.prb.uscourts.gov/doc1/158029925164, 5890, None"
    cnxn = db_login()
    cursor = cnxn.cursor()
    if pdr != None:
        logger.info(f"MySQL insert_docket_entry_file: running PDR")
        for p in pdr:
            if 'pdf_doc_files' in pdr[p]:
                for f in pdr[p]['pdf_doc_files']:
                    degl_res = doc_table_get_id(cnxn, f['link'], pdr[p]['dci_id'])
                    logger.debug(f"insert_docket_entry_file: degl_res: {degl_res}")
                    if degl_res:
                        dkt_e_id = degl_res[0][0]
                        dkt_e_name = f'Main Document - {degl_res[0][1]}'
                        dkt_e_link = f['link']
                        dkt_case_id = pdr[p]['dci_id']
                        try:
                            sql = """INSERT INTO docket_entry_file_links (docket_entry_id, docket_entry_name, docket_entry_link, docket_case_id)
                            VALUES (%s, %s, %s, %s)"""
                            val = (dkt_e_id, dkt_e_name, dkt_e_link, dkt_case_id)
                            cursor.execute(sql, val)
                            cnxn.commit()
                            logger.debug('MySQL: insert_docket_entry_file commit successful!')
                        except Exception as e:
                            logger.warning(f"insert_docket_entry_file commit FAILED: {e}")
            else:
                logger.debug(f"MySQL insert_docket_entry_file: no pdf_doc_files found(might be a case refresh)")
    else:
        logger.info(f"MySQL insert_docket_entry_file: download insert")
        try:
            if dkt_e_id:
                logger.info(f"MySQL insert_docket_entry_file: download insert: ID was passed, skipping look up - {dkt_e_id}")
            else: #[(127031, 'Pre-Petition Statement Pursuant to')] https://ecf.nyeb.uscourts.gov/doc1/122027872827 5933
                degl_res = doc_table_get_id(cnxn, dkt_e_link, dkt_case_id)
                logger.debug(f"degl_res: {degl_res}")
                if degl_res:
                    dkt_e_id = degl_res[0][0]
                    dkt_e_name = f"{dkt_e_name} - {degl_res[0][1]}"
            sql = """INSERT INTO docket_entry_file_links (docket_entry_id, docket_entry_name, docket_entry_link, docket_case_id)
            VALUES (%s, %s, %s, %s)"""
            val = (dkt_e_id, dkt_e_name, dkt_e_link, dkt_case_id)
            cursor.execute(sql, val)
            cnxn.commit()
            logger.debug('MySQL: insert_docket_entry_file commit successful!')
        except Exception as e:
            logger.warning(f"insert_docket_entry_file commit FAILED: {e}: {dkt_e_id}")
            pass
    cursor.close()         

def insert_company_ein(cnxn, data_201_results, pacer_data_results):
    cursor = cnxn.cursor()
    for k in data_201_results:
        comp_scrub = company_scrub(k)
        company_slug = create_company_slug(comp_scrub)
        check_result_company = check_if_company_exists(cnxn, company_slug)
        if check_result_company is not None:
            company_name = check_result_company
        else:
            company_name = title(comp_scrub)
        check_result_company = check_if_company_info_exists(cnxn, k)        
        try:
            sql = """INSERT INTO company_ein_number (name, ein)
            VALUES (%s, %s)"""
            val = (company_name, data_201_results[k]['ein_number'])
            cursor.execute(sql, val)
            cnxn.commit()
            logger.debug('MySQL: company_ein commit successful!')

        except Exception as e:
            logger.warning(f"insert_company_ein commit FAILED: {e}: {k}")
            logger.debug(k)
            pass

def insert_data_b201d(cnxn, data_201_results, pacer_data_results):
    cursor = cnxn.cursor()
    for k in data_201_results:
        try:#data_201_results[k]['naics_code']
            ncode_id = look_naics_key(data_201_results[k]['naics_code'])
            e_c_id = lookup_c(cnxn, data_201_results[k]['estimated_creditors_min'])
            e_a_id = lookup_a_l(cnxn, data_201_results[k]['estimated_assets_min'])
            e_l_id = lookup_a_l(cnxn, data_201_results[k]['estimated_liabilities_min'])

            sql = """INSERT INTO bankruptcy_201_data (estimated_creditors, estimated_assets, estimated_liabilities, naics_code, filing_id)
            VALUES (%s,%s,%s,%s,%s)"""
            val = (e_c_id, e_a_id, e_l_id, ncode_id, pacer_data_results[k]['bkw_filing_id'])

            cursor.execute(sql, val)
            cnxn.commit()
            logger.debug('MySQL: bankruptcy_201_data commit successful!')
        except Exception as e:
            logger.warning('bankruptcy_201_data commit FAILED: ' + str(e))
            logger.debug(k)
            logger.debug(data_201_results)
            pass

def insert_data_b204206d(cnxn, unsecured_creditor_name, unsecured_creditor_zip, unsecured_creditor_nature_of_claim, unsecured_creditor_claim_value, unsecured_creditor_industry, case_filing_id):
    cursor = cnxn.cursor()
    comp_scrub = company_scrub(unsecured_creditor_name)
    company_slug = create_company_slug(comp_scrub)
    check_result_company = check_if_company_exists(cnxn, company_slug)
    if check_result_company is not None:
        cred_title_comp = check_result_company
    else:
        cred_title_comp = title(comp_scrub)
    try:
        ncode_id = look_naics_key(unsecured_creditor_industry)
        sql = """INSERT INTO bankruptcy_204206_data (creditor_name, creditor_zip, nature_of_claim, unsecured_claim, industry, filing_id)
        VALUES (%s,%s,%s,%s,%s,%s)"""
        val = (cred_title_comp, unsecured_creditor_zip, unsecured_creditor_nature_of_claim.upper(), unsecured_creditor_claim_value, ncode_id, case_filing_id)
        cursor.execute(sql, val)
        cnxn.commit()
        logger.debug('MySQL: bankruptcy_204206_data commit successful!')
    except:
        try:
            ncode_id = look_naics_key(unsecured_creditor_industry)
            sql = """INSERT INTO bankruptcy_204206_data (creditor_name, creditor_zip, nature_of_claim, unsecured_claim, industry, filing_id)
            VALUES (%s,%s,%s,%s,%s,%s)"""
            val = (cred_title_comp, None, unsecured_creditor_nature_of_claim.upper(), unsecured_creditor_claim_value, ncode_id, case_filing_id)
            cursor.execute(sql, val)
            cnxn.commit()
            logger.debug('MySQL: bankruptcy_204206_data commit successful!')
        except Exception as e:
            logger.warning(f'bankruptcy_204206_data commit FAILED: {e}: {cred_title_comp} - {unsecured_creditor_zip}')
            pass

def insert_data_additional_info(cnxn, unsecured_creditor_name, unsecured_creditor_email, unsecured_creditor_phone, filing_id):
    cursor = cnxn.cursor()
    comp_scrub = company_scrub(unsecured_creditor_name)
    company_slug = create_company_slug(comp_scrub)
    check_result_company = check_if_company_exists(cnxn, company_slug)
    if check_result_company is not None:
        cred_title_comp = check_result_company
    else:
        cred_title_comp = title(comp_scrub)    
    try:
        sql = """INSERT INTO additional_info (email_address, phone_number, company_name, filing_id)
        VALUES (%s,%s,%s,%s)"""
        val = (unsecured_creditor_email, unsecured_creditor_phone, cred_title_comp, filing_id)
        cursor.execute(sql, val)
        cnxn.commit()
        logger.debug('MySQL: additional_info commit successful!')
    except Exception as e:
        logger.warning('additional_info commit FAILED: ' + str(e))
        logger.debug(cred_title_comp)
        pass

def look_naics_key(ncode):
    ncode_id = None
    first_three_chars = None
    first_two_chars = None
    try:
        first_three_chars = ncode[0:3]
    except:
        pass

    try:
        first_two_chars = ncode[0:2]
    except:
        pass
    prefix_object = lookup_naics_prefixes()
    for i in prefix_object:
        code_list = i['naics_codes'].split(',')
        if ncode == None:
            pass
        elif str(first_three_chars) in code_list:
            ncode_id = i['id']
            return(ncode_id)
        elif str(first_two_chars) in code_list:
            ncode_id = i['id']
            return(ncode_id)
        elif isinstance(ncode, int):
            ncode_id = 13
        else:
            ncode_id = None
    return(ncode_id)

def lookup_c(cnxn, min):
    cursor = cnxn.cursor()
    sql = """SELECT id FROM estimated_creditors WHERE min = %s"""
    cursor.execute(sql, [min])
    row = cursor.fetchone()
    if not row is None:
        try:
            logger.debug("Found: " + str(min) + " in estimated_creditors")
            return(str(row[0]))
        except:
            logger.debug("Unable to find: " + str(min) + " in + estimated_creditors")
    else:
        logger.debug("Entry does not exist: " + str(min) + " in estimated_creditors")
    return(None)

def lookup_a_l(cnxn, min):
    cursor = cnxn.cursor()
    sql = """SELECT id FROM estimated_assets WHERE min = %s"""
    cursor.execute(sql, [min])
    row = cursor.fetchone()
    if not row is None:
        try:
            logger.debug("Found: " + str(min) + " in estimated_assets")
            return(str(row[0]))
        except:
            logger.debug("Unable to find: " + str(min) + " in estimated_assets")
    else:
        logger.debug("Entry does not exist: " + str(min) + " in estimated_assets")
    return(None)

##############################################################################################

### ONE OFFS TO MANAGE DB / TEST ENTRIES ETC... ###
def readin_file():
    pd.set_option('max_columns', None)
    pd.set_option('max_rows', 3)

    df = pd.read_excel('../bankruptcy_filing_query_data.xlsx')
    df1 = df.replace(np.nan, 'NA', regex=True)
    return(df1)

def update_industry_ids(cnxn):
    cursor = cnxn.cursor()
    industry_data_results = None
    sql = """SELECT id,naics_desc,associated_names FROM industry_desc"""
    cursor.execute(sql)
    industry_data_results = cursor.fetchall()

    sql = """SELECT * FROM companies WHERE industry_attempted = 0 LIMIT 250"""
    cursor.execute(sql)
    comapny_data_results = cursor.fetchall()

    count = 0
    for i in industry_data_results:
        quick_list = []
        if i[2] is None:
            pass
        else:
            quick_list = i[2].split(',')
            quick_list.append(i[1])
        for q in quick_list:
            for c in comapny_data_results[:]:
                #print(f"C: {c[0]}")
                print(f"q: {q}, c: {c[0]}")
                wb_find = c[0].lower().find(q.strip().lower())
                count =+ 1
                if wb_find != -1:
                    print(f"WB Find: {c[0]}, {i[1]}, {i[0]}")
                    try:
                        sql = """UPDATE companies SET industry_id = %s, industry_attempted = 1 WHERE name = %s"""
                        val = (i[0], c[0])
                        cursor.execute(sql, val)
                        cnxn.commit()
                        del (comapny_data_results[count])
                        comapny_data_results[:] = comapny_data_results
                        print(f"Update industry by word bank successful")
                    except Exception as e:
                        logger.warning(f"Update industry by word bank FAILED: {e} {c}")
                        pass
#################################################################################

def main():
    #create_company_slug('hwy 55 tree & service--llc')
    connection = db_login()
    #pdr = {"AAA Environmental Inc": {"court_id": "caeb", "date_filed": "2022-12-07", "cs_year": "2022", "cs_number": "12083", "case_number": "1:2022bk12083", "cs_office": "1", "cs_chapter": "7", "case_link": "https://ecf.caeb.uscourts.gov//cgi-bin/iqquerymenu.pl?664032", "pdf_dl_status": "incomplete", "skip_201_parse": False, "skip_204_parse": False, "docket_table": ["12/07/2022:bkwsplit:https://ecf.caeb.uscourts.gov/doc1/032047979156:bkwsplit:26:bkwsplit:None:bkwsplit:  Chapter 7 Voluntary Petition Non-Individual filed. (Fee Paid $0.00) (Patrick Kavanagh) (eFilingID: 7156673) (Entered: 12/07/2022):bkwsplit:None", "12/07/2022:bkwsplit:None:bkwsplit:None:bkwsplit:None:bkwsplit:  Meeting of Creditors to be held on 1/6/2023 at 09:00 AM. See our website for location. (Scheduled Automatic Assignment, shared account) (Entered: 12/07/2022):bkwsplit:None", "12/07/2022:bkwsplit:https://ecf.caeb.uscourts.gov/doc1/032047979159:bkwsplit:3:bkwsplit:None:bkwsplit:  Master Address List (auto) (Entered: 12/07/2022):bkwsplit:None", "12/07/2022:bkwsplit:https://ecf.caeb.uscourts.gov/doc1/032047979183:bkwsplit:1:bkwsplit:None:bkwsplit:  Notice of Appointment of Interim Trustee Jeffrey M. Vetter (auto) (Entered: 12/07/2022):bkwsplit:None", "12/07/2022:bkwsplit:https://ecf.caeb.uscourts.gov/doc1/032047979272:bkwsplit:26:bkwsplit:None:bkwsplit:  Statement Regarding Ownership of Corporate Debtor/Party. See page 26 of Voluntary Petition (wmim) (Entered: 12/07/2022):bkwsplit:None", "12/08/2022:bkwsplit:None:bkwsplit:None:bkwsplit:None:bkwsplit:  Chapter 7 Voluntary Petition (Filing Fee Paid: $338.00, Receipt Number: 379546, eFilingID: 7156673) (auto) (Entered: 12/08/2022):bkwsplit:None", "12/08/2022:bkwsplit:https://ecf.caeb.uscourts.gov/doc1/032047982984:bkwsplit:1:bkwsplit:None:bkwsplit:  BNC 341 Notice Requested (CMX) (auto) (Entered: 12/08/2022):bkwsplit:None", "12/10/2022:bkwsplit:https://ecf.caeb.uscourts.gov/doc1/032047986636:bkwsplit:3:bkwsplit:None:bkwsplit:  Certificate of Mailing of Notice of Meeting of Creditors as provided by the Bankruptcy Noticing Center (Admin.) (Entered: 12/10/2022):bkwsplit:None"], "pdf_dl_skip": False, "pdf_dl_status_201": "complete", "pdf_dl_status_204206": None, "company_address": "220 uccello dr", "company_city": "las vegas", "company_state": "nv", "company_zip": "89158", "company_industry": "Unknown", "pdf_doc_files": ["caeb.2022bk12083.664032-petition.pdf"], "case_name": "AAA Environmental Inc", "parse_201_attempt": True, "parse_204206_attempt": True, " california contractor state lic board atton: bankruptcy 9821 business park drive sacramento, ca 95827__4pvnEyL9KyhdPFDdTYqPit__": {"industry": None, "nature_of_claim": "na", "unsecured_claim_value": "0.00", "creditor_company_name": "california contractor state lic board atton bankruptcy", "creditor_company_state": "ca", "creditor_company_zip": "95827"}, " franchise tax board bankruptcy section msa340 p.o. box 2952 sacramento, ca 95812__7V2kwuEZW6FheKcVbQeUna__": {"industry": None, "nature_of_claim": "na", "unsecured_claim_value": "46000.00", "creditor_company_name": "franchise tax board bankruptcy section msa340", "creditor_company_state": "ca", "creditor_company_zip": "95812"}, " internal revenue service insolvency section p.o. box 7346 philadelphia, pa 19101__PuRczzg4onEBhb8rwxfKgn__": {"industry": None, "nature_of_claim": "na", "unsecured_claim_value": "80000.00", "creditor_company_name": "internal revenue service insolvency section", "creditor_company_state": "pa", "creditor_company_zip": "19101"}, "employment development department bankruptcy/special procedures p. o. box 826880, mic: 92e sacramento, ca 94280__kzLuoa9FkEGkj7EYcuL2ZH__": {"industry": None, "nature_of_claim": "na", "unsecured_claim_value": "43056.85", "creditor_company_name": "employment development department bankruptcy/special procedures", "creditor_company_state": "ca", "creditor_company_zip": "94280"}, "sherwin williams atton: bankruptcy 101 w. prospect ave cleveland, oh 44150__b4NNHazMarNFU3uwokN54M__": {"industry": None, "nature_of_claim": "store credit", "unsecured_claim_value": "1700.00", "creditor_company_name": "sherwin williams atton bankruptcy", "creditor_company_state": "oh", "creditor_company_zip": "44150"}, "u.s. small business administration legal division - district office 6501 sylvan road #100 citrus heights, ca 95610__k5qLc3WicCdM8bMghQhq9Q__": {"industry": None, "nature_of_claim": "na", "unsecured_claim_value": "150000.00", "creditor_company_name": "u.s. small business administration legal division district office", "creditor_company_state": "ca", "creditor_company_zip": "95610"}, "united rentals atton: bankruptcy 100 fisrt stamford place ste 700 stamford, ct 06902__EP7NyMmSgJWf9B4dkSSnqe__": {"industry": None, "nature_of_claim": "equipment rental", "unsecured_claim_value": "14000.00", "creditor_company_name": "united rentals atton bankruptcy", "creditor_company_state": "ct", "creditor_company_zip": "06902"}}}
    #print(check_if_company_info_exists(connection, 'AAA Environmental Inc'))
    #insert_data_dci(connection, pdr)
    #print(company_scrub('$ Alert Protective Services Inc'))
    ids = [127201, 127420, 127455]
    remove_old_docket_entry_if_exist(ids)
    #connection = db_login()
    #prefix_object = lookup_naics_prefixes()
    #for i in prefix_object:
    #    code_list = (i['naics_codes'].split(','))
    #    if '33' in code_list:
    #        print(i['id'])
    #print(look_naics_key(33))
    #connection.close()


# MAIN
if __name__ == '__main__':
    main()
