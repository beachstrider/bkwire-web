import datetime
import requests
import time
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ManufacturingNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://manufacturing.einnews.com/search/bankruptcy/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            ul_tag = soup.find("ul", class_="pr-feed")
            for li in ul_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3").text.strip()
                news_dict["Link"] = ("https://manufacturing.einnews.com" + li.find("h3").find("a", href=True)["href"])
                news_dict["Snippet"] = li.find("p", class_="excerpt").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            url = "https://www.manufacturing.net/search/?q=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "gs-title")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all("div", limit=3, class_="gsc-webResult gsc-result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div",class_="gs-title").text.strip()
                news_dict["Link"] = div.find("div",class_="gs-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[1].strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.americanmanufacturing.org/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="block-search-result post"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="post-title").text.strip()
                news_dict["Link"] = div.find("h2", class_="post-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="post-excerpt").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="date-circle").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            url = "https://www.industryweek.com/search?filters={%22text%22:%22Manufacturing%20bankruptcy%22,%22type%22:[],%22websiteSchedule%22:[],%22labels%22:[],%22authors%22:[]}"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "date")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all("div", limit=2, class_="item medium"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = ("https://www.industryweek.com" + div.find("h3").find_parent("a", href=True)["href"])
                news_dict["Snippet"] = div.find("div", class_="teaser-text").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.assemblymag.com/search?page=1&q=bankruptcy&sort=date",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=3, class_="record"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="headline").text.strip()
                news_dict["Link"] = div.find("h2", class_="headline").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="abstract").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://www.manufacturingusa.com/search?k=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="views-row"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="field-title").text.strip()
                news_dict["Link"] = (
                    "https://www.manufacturingusa.com"
                    + div.find("div", class_="field-title").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("div", class_="field-summary").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)
            logging.error("Your search did not return any results.")

        # Seventh Website
        try:
            response = requests.get(
                "https://www.autonews.com/search?search_phrase=bankruptcy&field_emphasis_image=&sort_by=search_api_relevance",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="views-field views-field-nothing"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a").text.strip()
                news_dict["Link"] = ("https://www.autonews.com" + div.find("a", href=True)["href"])
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span", class_="updated").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eighth Website
        # Selenium Driver Headless Chrome
        url = "https://www.aerospacemanufacturinganddesign.com/search/index/?&searchTerm=bankruptcy&searchOrderBy=date"
        options = Options()
        options.headless = True
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
        driver.get(url)
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "caption")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            for div in soup.find_all("div", limit=3, class_="result mb-15"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = ("https://www.aerospacemanufacturinganddesign.com" + div.find("h3").find("a", href=True)["href"])
                news_dict["Snippet"] = div.find("p", class_="caption").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span", class_="date text-muted").text.split("-")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"Site have lazy loading proccess {exception_msg}")

        return news_list