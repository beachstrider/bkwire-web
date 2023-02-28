import datetime
import requests
import logging
from bs4 import BeautifulSoup
import dateparser
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 


class BusinessServicesNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
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

        # Second Website
        try:
            url = "https://americanstaffing.net/?s=bankruptcy#pagesAndArticles"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-page-result")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for li in soup.find_all("li", limit=1, class_="search-page-result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h4").text.strip()
                news_dict["Link"] = li.find("h4").find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("div", class_="search-page-result__excerpt").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third website
        try:
            response = requests.get(
                "https://www.accountingtoday.com/search?q=bankruptcy&f0=00000154-ca96-d983-a9dc-eebfcad90000",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=4, class_="PromoMediumImageLeft-content"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="PromoMediumImageLeft-title").text.strip()
                news_dict["Link"] = div.find("div", class_="PromoMediumImageLeft-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                try:
                    news_dict["date"] = dateparser.parse(
                        div.find("div", class_="PromoMediumImageLeft-timeSince").text,settings={'TIMEZONE': 'UTC'}
                    ).strftime("%Y-%m-%d")
                except:
                    news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth website
        try:
            response = requests.get(
                "https://www.journalofaccountancy.com/search.html?_charset_=UTF-8&q=bankruptcy&language=en",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=4):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h1").text.strip()
                news_dict["Link"] = ("https://www.journalofaccountancy.com" + article.find("a", href=True)["href"])
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = dateparser.parse(article.find("div", class_="date-time")["data-time"].split("T")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth website
        try:
            response = requests.get(
                "https://www.cpajournal.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=4):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = article.find("a", href=True)["href"]
                snippet_div_tag = article.find("div", class_="newsmag-content entry-content")
                news_dict["Snippet"] = snippet_div_tag.find("p").text.strip()
                news_dict["date"] = dateparser.parse(article.find("div", class_="meta").text.splitlines()[-2],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth website
        try:
            response = requests.get(
                "https://www.fm-magazine.com/search.html?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", class_="resource-list-item", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.fm-magazine.com" + article.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find(
                    "p", class_="resource-list-item__description"
                ).text.strip()
                news_dict["date"] = dateparser.parse(article.find("span", class_="resource-list-item__date formatted-date")["data-date"].split("T")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh website
        try:
            response = requests.get(
                "https://www.thesoftwarereport.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="item-details"):
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

        # Eighth website
        try:
            url = "https://www.natlawreview.com/nlr-legal-analysis-and-news-database-search?qnlr=bankruptcy#gsc.tab=0&gsc.q=bankruptcy&gsc.sort=date"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "gs-title")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all("div", limit=2, class_="gsc-webResult gsc-result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div",class_="gs-title").text.strip()
                news_dict["Link"] = div.find("div",class_="gs-title").find("a", href=True)["href"]
                snippet_data = div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[1:]
                news_dict["Snippet"] = " ".join(snippet_data).strip()
                news_dict["date"] = dateparser.parse(
                                    div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[0],settings={'TIMEZONE': 'UTC'}
                                    ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Nineth website
        try:
            response = requests.get(
                "https://www.law360.com/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", class_="hnews hentry", limit=4):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.law360.com" + li.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li.find("p").text.strip()
                news_dict["date"] = dateparser.parse(li.find("span")["title"],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list
