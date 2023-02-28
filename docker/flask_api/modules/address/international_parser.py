import re
import os
import usaddress
import logging.config
from logtail import LogtailHandler
from curses.ascii import isdigit
from os import listdir, path
from postal.parser import parse_address

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

class IntAddyParse:
    def __init__(self):
        self.addy_parse = None

    def parse_address(self, addy):
        if re.search(r'^[0-9]{1,2}',addy):
            addy = re.sub(r'^[0-9]{1,2}', '', addy)        

        house, house_number, city, state, postcode, road = None, None, None, None, None, None
        comp_name_found = re.search('^(.+? inc)|(.+? llc)|(.+? corp)|(.+? company)\
            |(.+? corporation)|(.+? ltd)|(.+? pllc)|(.+? lp)', addy)
        if comp_name_found:
            house = comp_name_found[0]
            address = addy.replace(str(comp_name_found[0]), '').lstrip()
        else:
            comp_name_fixed = re.split('(?i)attn:|attn|c\/o|esq\.|esq|esquire',addy)
            
            if len(comp_name_fixed) > 1:
                house = comp_name_fixed[0]
                address = comp_name_fixed[1]
            else:
                address = comp_name_fixed[0]

        results = (parse_address(address))
        search_tuple = dict(results)
        for s,t in search_tuple.items():
            st = s.replace("$","").replace(",","")
            if t == 'house' and house == None:
                b = s.find('basis')
                p = s.find('as of the petition')                
                if b != -1:
                    pass
                elif p != -1:
                    pass
                elif st.isdigit():
                    pass
                else:
                    house = s
            if t == 'house_number':
                house_number = s
            if t == 'city':
                city = s
            if t == 'state':
                state = s
            if t == 'postcode':
                postcode = s
            if t == 'road':
                road = s 
        if house == None:
            try:
                adr = usaddress.tag(addy)
            except Exception as e:
                logger.error(f"USAddress parsing failed: {e}: {addy}")
            try:
                house = adr[0]['BuildingName']
            except:
                pass
            try:
                house = adr[0]['Recipient']
            except:
                pass
            try:
                house = adr[0]['SubaddressType']
            except:
                pass            
        return(house, house_number, state, postcode, city, road)

def main():
    iap = IntAddyParse()
    iap_results = iap.parse_address('25 KWI 2200 Northern Blvd, Ste 102 Greenvale, NY 11548')
    print(iap_results)


# MAIN
if __name__ == '__main__':
    main()