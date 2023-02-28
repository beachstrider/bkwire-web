#!/usr/bin/python
import re
import os,sys
import time
from os import path
from logtail import LogtailHandler
import logging.config
import spacy
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
## IMPORT CUSTOM MODULES ##
sys.path.insert(0, '/app')
from modules.database.db_select import dbSelectItems
from modules.industry.industry_scraper import WebScrape

nlp = spacy.load("en_core_web_sm")

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


class UpdateIndustry:
    def __init__(self):
        logger.info('Running industry updater...')
        self.db1 = dbSelectItems()
        self.db1.db_login()
        sql_query = "SELECT * FROM companies WHERE industry_id is NULL AND industry_attempted = False;"
        #sql_query = "SELECT * FROM companies WHERE name = 'Black Knight Financial Services, Inc.';"
        self.comps_no_industry = self.db1.fetch_no_cache(sql_query)
        self.naics_db_info = self.db1.fetch_no_cache(f"SELECT * FROM industry_desc")
        self.industry_desc_words = self.db1.fetch_no_cache(f"SELECT associated_names FROM industry_desc")
        self.all_keys = []
        self.ind_d_works = []
        
        self.whats_left = {}        
        self.person_dict = {}
        self.company_list = {}
        self.everything_else = {}
    #Code "borrowed" from somewhere?!
    def entities(self,text):
        mtext = f"{text} is looking to make a move"
        doc = nlp(mtext)
        # Analyze syntax
        #print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
        #print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])
        regex_list = []
        reg_find_list_end = ['inc\.', 'corp\.', 'llc\.', 'l\.l\.c\.', 'co\.', 'ltd\.', 'pllc\.', \
        'lp\.', 'l\.p\.']
        reg_find_list_end_no_space = ['inc\.', 'corp\.', 'llc\.', 'l\.l\.c\.', 'ltd\.', 'pllc\.']
        reg_find_list_any = ['corporation', 'incorporated', 'limited', 'company', \
         'financial', 'non-profit', 'nonprofit', 'incorporado', 'organization', \
         'dba', 'd/b/a', 'trust', 'school', 'american', 'associates', 'group', \
         'system', 'enterprise', 'services', 'restaurant', 'partnership', 'commercial', \
         'industrial', 'properties', 'products', 'holdings', 'construction', 'environment', \
         'community', 'baptist', 'international']

        for i in self.industry_desc_words:
            if i['associated_names'] == None:
                pass
            else:
                words = i['associated_names'].split(',')
                for w in words:
                    self.ind_d_works.append(w.strip())

        for l in reg_find_list_end:
            regex_list.append(rf".+?[\w\,] {l}?$""")

        for l in reg_find_list_end_no_space:
            regex_list.append(rf".+?[\w\,]{l}?$""")

        for l in reg_find_list_any:
            regex_list.append(rf".*{l}.*""")

        for l in self.ind_d_works:
            regex_list.append(rf".*{l}.*""")

        for entity in doc.ents:
            for regex in regex_list:
                s = re.search(regex, str(text), re.IGNORECASE)
                if s:
                    self.company_list[str(text)] = 1
                elif entity.label_ == 'PERSON':
                    self.person_dict[str(text)] = 1
                else:
                    self.whats_left[str(text)] = 1
        self.everything_else[str(text)] = 1

    def check_industry_word_bank(self, comp_name):
        # Init the DB
        result = None
        ncode_id = ['30', 'Not Found']
        #run company crawl#
        if comp_name != None:
            logger.info(f'Checking industry word bank: {comp_name}')

#            ws1 = WebScrape()
#            result = ws1.get_industry_type_from_linkedin_search(comp_name)
#            if result == None:
#                result = ws1.get_industry_type_from_ein(comp_name)
#            if result == None:
#                result = ws1.get_industry_type_from_wikipedia(comp_name)
#            if result == None:
#                result = ws1.get_industry_type_from_dnb(comp_name)
#            if result == None:
#                result = ws1.get_industry_type_from_google(comp_name)
#            #company_data[comp_name] = result
#            ws1.driver.quit()

            for i in self.naics_db_info:
                compare_company_name = comp_name.lower().lstrip()
                compare_naics_name = i['naics_desc'].lower().lstrip()
                if not compare_company_name.find(compare_naics_name) == -1:
                    nc = i['naics_codes'].split(',')
                    logger.debug(f"Word Bank Find: {compare_company_name}: {i['id']}")
                    ncode_id = (i['id'], compare_naics_name)
                elif not i['associated_names'] == None:
                    ass_names_list = i['associated_names'].split(',')
                    for a in ass_names_list:
                        compare_naics_alias = a.lower().lstrip()
                        if not compare_company_name.find(compare_naics_alias) == -1:
                            nc = i['naics_codes'].split(',')
                            logger.debug(f"Word Bank Find: {compare_company_name}: {i['id']}")
                            ncode_id = (i['id'], compare_naics_alias)

                        #if result != None:
                            #industry_name_found = result.lower().lstrip()
                            #if not industry_name_found.find(compare_naics_alias) == -1:
                                #nc = i['naics_codes'].split(',')
                                #logger.debug(f"Word Bank Find: {compare_company_name}: {i['id']}")
                                #ncode_id = (i['id'], compare_naics_alias)
#                                
                #elif result != None:
                    #compare_naics_name = i['naics_desc'].lower().lstrip()
                    #industry_name_found = result.lower().lstrip()
                    #if not industry_name_found.find(compare_naics_name) == -1:
                        #nc = i['naics_codes'].split(',')
                        #logger.debug(f"Word Bank Find: {compare_company_name}: {nc[0]}")
                        #ncode_id = (i['id'], compare_naics_alias)

            comp_slug = comp_name.replace(' ', '-')
            if ncode_id != None:
                sql = f"UPDATE `companies` SET industry_id = '{ncode_id[0]}', industry_attempted = True, industry_captured = '{ncode_id[1]}' WHERE slug = '{comp_slug}'"
                logger.debug(self.db1.sql_commit(sql))
            else:
                sql = f"UPDATE `companies` SET industry_attempted = True WHERE slug = '{comp_slug}'"
                logger.debug(self.db1.sql_commit(sql))
        else:
            pass

    def runit(self):
        start = time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            for i in self.comps_no_industry:
                fix_slug = i['slug'].replace('-', ' ')
                self.entities(fix_slug)
                #processes.append(executor.submit(ui.entities, fix_slug))
                #industry = processes.append(executor.submit(ui.check_industry_word_bank, fix_slug))
                #ui.check_industry_word_bank(fix_slug)

        logger.info(f"New industry comp list: {self.company_list}: {len(self.company_list)}")
        for u in self.company_list:
            if u in self.person_dict.keys():
                del self.person_dict[u]

            if u in self.whats_left.keys():
                del self.whats_left[u]
            self.all_keys.append(u)
            self.check_industry_word_bank(u)

        logger.info(f"New industry person list: {self.person_dict}: {len(self.person_dict)}")
        for p in self.person_dict:
            fix_slug_back = p.replace(' ', '-')
            self.all_keys.append(p)
            sql = f"UPDATE `companies` SET industry_id = '7', industry_attempted = True, industry_captured = 'investor' WHERE slug = '{fix_slug_back}'"
            logger.debug(self.db1.sql_commit(sql))

        logger.info(f"New industry whats left list: {self.whats_left}: {len(self.whats_left)}")
        for w in self.whats_left:
            self.all_keys.append(w)
            self.check_industry_word_bank(w)

        for a in self.all_keys:
            if a in self.everything_else.keys():
                del self.everything_else[a]

        logger.info(f"New industry everything else list: {self.everything_else}: {len(self.everything_else)}")
        for e in self.everything_else:
            self.check_industry_word_bank(e)

        print(f'Time taken: {time() - start}')
        #print(company_industry_dic)


# MAIN
if __name__ == '__main__':
    main()
