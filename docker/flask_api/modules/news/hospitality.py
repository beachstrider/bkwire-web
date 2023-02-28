import datetime
import requests
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC    


class HospitalityNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        # Selenium Driver Headless Chrome
        try:
            url = "https://americanstaffing.net/?s=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-page-result")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for li in soup.find_all("li", limit=2, class_="search-page-result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h4").text.strip()
                news_dict["Link"] = li.find("h4").find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("div", class_="search-page-result__excerpt").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.hospitalitynet.org/search.html?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find(
                "div", class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-16"
            )
            for article in soup.find_all("article", limit=2, class_="list-item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h1").text.strip()
                news_dict["Link"] = (
                    "https://www.hospitalitynet.org"
                    + article.find("h1").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = dateparser.parse(article.find("time").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website 
        try:
            url = "https://www.cnbc.com/search/?query=Hospitality%20bankruptcy&qsearchterm=Hospitality%20bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "resultlink")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            div_tag = soup.find("div",attrs={"id":"searchcontainer"})
            for div in div_tag.find_all("div", limit=6, class_="SearchResult-searchResultContent"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a", class_="resultlink").text.strip()
                news_dict["Link"] = div.find("a", href=True, class_="resultlink")["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span", class_="SearchResult-publishedDate").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://skift.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="story-content"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = div.find("a", href=True, class_="story-link")["href"]
                news_dict["Snippet"] = div.find("p", class_="skift-take").text.split("...")[1].strip()
                news_dict["date"] = dateparser.parse(div.find("p", class_="skift-take").text.split("...")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://lodgingmagazine.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="td_module_1 td_module_wrap td-animation-stack"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = div.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("h3").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://www.nrn.com/search/node/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div",class_="search-results__results")
            for article in div_tag.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("div", class_="title").text.strip()
                news_dict["Link"] = ("https://www.nrn.com" + article.find("a", href=True)["href"])
                news_dict["Snippet"] = article.find("div", class_="summary").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("span", class_="date-display-single").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eigth Website
        try:
            response = requests.get(
                "https://www.qsrmagazine.com/search?search=bankruptcy&sort_by=created&sort_order=DESC",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div",attrs={"id":"block-qsr2020-content"})
            for div in div_tag.find_all("div", limit=2, class_="views-row"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="views-field views-field-title search-title").text.strip()
                news_dict["Link"] = (
                    "https://www.qsrmagazine.com" + div.find("div", class_="views-field views-field-title search-title").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("div", class_="views-field views-field-search-api-excerpt search-excerpt").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="views-field views-field-created search-date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Ninth Website
        try:
            response = requests.get(
                "https://www.hotel-online.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tags = soup.find_all("div", limit=3, class_="row")
            for div in div_tags:
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h1").text.strip()
                news_dict["Link"] = div.find("h1").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("h1").text.strip()
                news_dict["date"] = dateparser.parse(div.find("p").text.split("|")[1],settings={'TIMEZONE': 'UTC'}).strftime(
                    "%Y-%m-%d"
                )
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Tenth Website
        try:
            response = requests.get(
                "https://airlineweekly.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="article-thumb"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = (
                    div.find("div", class_="thumb-contents").find("a").text.strip()
                )
                news_dict["Link"] = div.find("div", class_="thumb-contents").find(
                    "a", href=True
                )["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 12th Website
        try:
            response = requests.get(
                "https://www.cruise-ship-industry.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2").text.strip()
                news_dict["Link"] = article.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("span", class_="updated").text.split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 13th Website
        try:
            response = requests.get(
                "https://hotelbusiness.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="col-lg-6 mb-4"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3", class_="entry-title").text.strip()
                news_dict["Link"] = div.find("h3", class_="entry-title").find(
                    "a", href=True
                )["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 14th Website
        try:
            response = requests.get(
                "https://staffinghub.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=1, class_="item-details"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = div.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="td-excerpt").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list