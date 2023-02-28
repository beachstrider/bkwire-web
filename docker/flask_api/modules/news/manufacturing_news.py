import datetime
import requests
import time
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ManufacturingNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://manufacturing.einnews.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            ul_tag = soup.find("ul", class_="pr-feed")
            for li in ul_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://manufacturing.einnews.com"
                    + li.find("h3").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li.find("p", class_="excerpt").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.manufacturing.net/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            aside_tag = soup.find_all("aside")[1]
            for div in aside_tag.find_all("div", limit=2, class_="node-list__node"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h5").text.strip()
                news_dict["Link"] = (
                    "https://www.manufacturing.net"
                    + div.find("h5").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("h5").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.americanmanufacturing.org/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="block-post-loop"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3", class_="post-loop-title").text.strip()
                news_dict["Link"] = div.find("h3", class_="post-loop-title").find(
                    "a", href=True
                )["href"]
                news_dict["Snippet"] = div.find("h3", class_="post-loop-title").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="post-loop-date-circle").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.industryweek.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="item medium"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.industryweek.com"
                    + div.find("a", class_="title-wrapper", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("h3").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.assemblymag.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="featured-news__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find(
                    "h1", class_="featured-news__headline"
                ).text.strip()
                news_dict["Link"] = li.find(
                    "a", class_="featured-news__article-title-link", href=True
                )["href"]
                news_dict["Snippet"] = li.find(
                    "div", class_="featured-news__teaser"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://www.manufacturingusa.com/news",
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

        # Seventh Website
        try:
            response = requests.get(
                "https://www.autonews.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="block-region-content-top")
            for div in div_tag.find_all("div", limit=2, class_="feature-article-headline"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a").text.strip()
                news_dict["Link"] = (
                    "https://www.autonews.com" + div.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("a").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eighth Website
        # Selenium Driver Headless Chrome
        url = "https://www.aerospacemanufacturinganddesign.com/news/"
        options = Options()
        options.headless = True
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
        driver.get(url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            for article in soup.find_all("article", limit=2, class_="mb-15"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.aerospacemanufacturinganddesign.com"
                    + article.find("h3").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find("p", class_="caption").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("span", class_="date text-muted").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"Site have lazy loading proccess {exception_msg}")

        return news_list
