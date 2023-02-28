import os
import re
import time
import urllib
import requests
from modules.industry import config
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class WebScrape:
    def __init__(self):
        # LinkedIn Creds
        self.options = Options()
        self.options.headless = True
        self.driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=self.options)

    def get_industry_type_from_linkedin_search(self, search_query):
        industry = None
        print("Searching LinkedIn...")
        # Prepare a search query for linkedin
        search_query = f"site:linkedin.com {search_query} industry type"

        query = urllib.parse.quote_plus(search_query)
        # session = HTMLSession()
        response = requests.get("https://www.google.com/search?q=" + query)

        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.findAll("div")

        for row in table:
            if "Industries:" in row.text:
                try:
                    result = re.search("Industries: (.*) Company size:", row.text)
                    if (
                        ";" in result.group(1)
                        and "."
                        not in result.group(1)[: result.group(1).find("Company size:")]
                    ):
                        industry = result.group(1).split(";")[0].strip()
                        break
                    else:
                        industry = result.group(1).split(".")[0]
                        break
                except:
                    continue
        return industry


    def get_industry_type_from_google(self, search_query):
        # Set default
        industry = None
        print("Searching Google...")
        # Selenium get the google URL
        query = urllib.parse.quote_plus(search_query)
        url = "https://www.google.com/maps/search/" + query
        self.driver.get(url)

        # Find for the company/industry type element and get the value.
        try:
            industry = self.driver.find_element(
                By.CSS_SELECTOR, "button[jsaction='pane.rating.category']"
            ).text
        except Exception as e:
            try:
                industry = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div:nth-child(3) > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div > div:nth-child(4) > div:nth-child(2) > span > jsl > span:nth-child(2)"
                ).text
            except:
                print("Industry not found on google business!")
                pass
        return industry

    def get_industry_type_from_ein(self, search_query):
        data = {}
        industry = None
        print("Searching Taxidein...")

        self.driver.get(config.EIN_TAX_ID_URL)
        try:
            elem = self.driver.find_element(By.ID, "searchterm")
            elem.clear()
            elem.send_keys(search_query)
        except:
            elem = self.driver.find_element(By.ID, 'searchtermid')
            elem.send_keys(search_query)
            elem.send_keys(Keys.RETURN)

        try:
            '''
            first checking on eintaxid websites for details
            '''
            WebDriverWait(self.driver, config.DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@id="resultHere"]/div[1]/div[1]/div/div/strong[1]')))
            company_name_link = self.driver.find_element(By.XPATH, '//*[@id="resultHere"]/div[1]/div[1]/div/div/a')
            company_name_link.click()
            WebDriverWait(driver, config.DELAY).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[2]/table[1]/tbody/tr[1]/th')))
            type_of_business = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[2]/table[1]/tbody/tr[4]/th').text
            if type_of_business == 'Type of business':
                industry = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[2]/table[1]/tbody/tr[4]/td').text
            else:
                raise ValueError("Industry not found")
        except Exception as e:
            # When eintaxid fails to find company
            pass

        return industry

    def get_industry_type_from_linkedin_search_logged_in(self, search_query):
        industry = None
        print("Searching LinkedIn Logged in...")

        self.driver.get(config.LINKEDIN_URL)
        try:
            signin = self.driver.find_element(By.XPATH, '/html/body/div[1]/main/p[1]/a')
            signin.click()
            email = self.driver.find_element(By.ID, 'username')
            email.send_keys(config.LINKEDIN_EMAIL)
            password = self.driver.find_element(By.ID, 'password')
            password.send_keys(config.LINKEDIN_PASSWORD)
            password.send_keys(Keys.RETURN)
        except:
            pass
        WebDriverWait(self.driver, config.LINKEDIN_WAIT).until(EC.presence_of_element_located((By.XPATH,
                '//*[@id="global-nav-typeahead"]/input')))
        search_button = self.driver.find_element(By.XPATH, '//*[@id="global-nav-search"]/div/button/li-icon')
        search_button.click()
        elem = self.driver.find_element(By.XPATH, '//*[@id="global-nav-typeahead"]/input')
        elem.clear()
        elem.send_keys(search_query)
        elem.send_keys(Keys.RETURN)
        try:
            WebDriverWait(self.driver, config.LINKEDIN_WAIT).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div/div[1]/div/a/div/div[1]/div[1]/div/div/span/span/a')))
            company_name_link = self.driver.find_element(By.XPATH, '//*[@id="main"]/div/div/div[1]/div/a/div/div[1]/div[1]/div/div/span/span/a')
            if company_name_link.text.lower() == search_query.lower():
                industry = self.driver.find_element(By.XPATH, '//*[@id="main"]/div/div/div[1]/div/a/div/div[1]/div[2]/div/div[1]').text
                industry = industry[:industry.index(" •")]
            else:
                print("Second Website failed to find too!")
        except Exception as e:
            # When LinkedIn fails to find company
            pass

        return industry

    def get_industry_type_from_wikipedia(self, search_query):
        industry = None
        print("Searching Wikipedia...")

        try:
            self.driver.get(config.WIKIPEDIA_URL)
            elem = self.driver.find_element(By.ID, 'searchInput')
            elem.send_keys(search_query)
            time.sleep(3)
            elem.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, config.DELAY).until(EC.presence_of_element_located((By.XPATH,
                    '//*[@id="mw-content-text"]/div[1]/table[1]/tbody/tr[7]/th')))
            company_name_link = self.driver.find_element(By.XPATH, '//*[@id="mw-content-text"]/div[1]/table[1]/caption')
            if company_name_link.text.lower() == search_query.lower():
                industry = self.driver.find_element(By.XPATH, '//*[@id="mw-content-text"]/div[1]/table[1]/tbody/tr[7]/td/div/ul').text
                industry = re.sub(r'([A-Z])', r', \1', re.sub(r'[,:=/]', '', industry))[1::]
        except Exception as e:
            # When LinkedIn fails to find company
            pass

        return industry

    def get_industry_type_from_dnb(self, search_query):
        industry = None
        print("Searching DnB...")

        try:
            self.driver.get(config.DNB_URL)
            search_button = self.driver.find_element(By.XPATH, '//*[@id="page"]/div[1]/div/div[1]/div[3]/div/div[3]/div[1]/button')
            search_button.click()
            search_elem = self.driver.find_element(By.XPATH, '//*[@id="page"]/div[1]/div/div[2]/div/div[3]/div/div/div/div/div[1]/input')
            search_elem.send_keys(search_query)
            search_elem.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, config.LINKEDIN_WAIT).until(EC.presence_of_element_located((By.XPATH,
                    '//*[@id="page"]/div[3]/div[1]/div/div/div[3]/div[2]/div[1]/div[2]/div[2]/div[2]/table/tbody/tr/td[1]/a[1]')))
            company_name_link = self.driver.find_element(By.XPATH, '//*[@id="page"]/div[3]/div[1]/div/div/div[3]/div[2]/div[1]/div[2]/div[2]/div[2]/table/tbody/tr/td[1]/a[1]')
            if company_name_link.text.replace(',', '').lower() == search_query.replace(',', '').lower():
                industry = self.driver.find_element(By.XPATH, '//*[@id="page"]/div[3]/div[1]/div/div/div[3]/div[2]/div[1]/div[2]/div[2]/div[2]/table/tbody/tr/td[2]/span').text
        except Exception as e:
            print("Company Not Found!")
            pass

        return industry


def main():
    company_data = {}
    companies = config.test_comps
    street = ""
    city = ""
    state = ""
    country = ""
    # Prepare a Search Query for Linkedin and Google.
    for company_name in companies:
        #company_name = f"{company_name} "
        search_query = company_name + " ".join([street, city, state, country])

        ws1 = WebScrape()
        result = ws1.get_industry_type_from_linkedin_search(search_query)
        if result == None:
            result = ws1.get_industry_type_from_ein(search_query)
        if result == None:
            result = ws1.get_industry_type_from_wikipedia(search_query)
        if result == None:
            result = ws1.get_industry_type_from_dnb(search_query)
        if result == None:
            result = ws1.get_industry_type_from_google(search_query)
        print(f"company: {company_name}, company_industry: {result}")
        company_data[company_name] = result
        ws1.driver.quit()

    print(company_data)

# MAIN
if __name__ == '__main__':
    main()
