import requests
import datetime
import logging
from bs4 import BeautifulSoup
import dateparser
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ChemicalNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.specchemonline.com/search/node?keys=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            post_container = soup.find("ol", class_="search-results node_search-results")
            for li in post_container.find_all("li"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3").text
                news_dict["Link"] = "https://www.specchemonline.com" + li.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("p").text
                news_dict["date"] = dateparser.parse(li.find_all("p")[1].text.split("-")[1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second website
        try:
            response = requests.get(
                "https://www.chemistryworld.com/searchresults?qkeyword=bankruptcy&PageSize=10&parametrics=&cmd=ChangeSortOrder&val=1&SortOrder=1",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            post_container = soup.find("div",class_="listBlocks",)
            for li in post_container.find_all("li",limit=4):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3").text
                news_dict["Link"] = li.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("h3").text
                news_dict["date"] = dateparser.parse(li.find("p",class_="meta").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third website
        try:
            response = requests.get(
                "https://www.echemi.com/searchGoods.html?keywords=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            post_container = soup.find(
                "div",
                class_="width_1260 cont",
            )
            news_list_container = post_container.find("div", class_="news_list")
            for li in news_list_container.find_all("li", limit=3):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("a").text
                news_link = li.find("a", href=True)
                news_dict["Link"] = news_link["href"]
                news_dict["Snippet"] = li.find("p").text
                news_dict["date"] = dateparser.parse(li.find("span").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error("Oops, the article couldn't be found!")

        # Fourth website
        # Selenium Driver Headless Chrome 
        try:
            url = "https://cen.acs.org/search.html?q=bankruptcy&sortBy=date&rpp=10&startYear=1998&startMonth=08&startDay=01&endYear=2022&endMonth=08&endDay=08&topics=all"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "topic-content-text")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            post_container = soup.find("div",attrs={"id":"search-result"})
            for div in post_container.find_all("div", limit=4, class_="grid-x"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text
                news_dict["Link"] = div.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find_all("p")[-2].text
                news_dict["date"] = dateparser.parse(div.find_all("p")[-1].text.split("|")[-1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        # Selenium Driver Headless Chrome
        try:
            url = "https://www.chemicalprocessing.com/site-search?q=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all("div", limit=2, class_="gsc-webResult gsc-result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div",class_="gs-title").text.strip()
                news_dict["Link"] = div.find("div",class_="gs-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[1].strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list
