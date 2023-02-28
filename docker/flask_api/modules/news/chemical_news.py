import requests
import datetime
import logging
from bs4 import BeautifulSoup
import dateparser
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ChemicalNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.specchemonline.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            post_container = soup.find(
                "div",
                class_="views-view-grid horizontal cols-2 clearfix",
            )
            for div in post_container.find_all("div", limit=3, class_="post-content"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a").text
                news_link = div.find("a", href=True)
                news_dict["Link"] = "https://www.specchemonline.com" + news_link["href"]
                news_dict["Snippet"] = div.find("p").text
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="post-created").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second website
        try:
            response = requests.get(
                "https://www.chemistryworld.com/section/business",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            post_container = soup.find(
                "div",
                class_="spinBlock colour3 hasnotitle",
            )
            news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
            h2_tag = post_container.find("h2")
            news_link = h2_tag.find("a", href=True)
            date_p_tag = post_container.find("p", class_="meta")

            news_dict["Title"] = h2_tag.find("a").text
            news_dict["Link"] = news_link["href"]
            news_dict["Snippet"] = post_container.find("p", class_="intro").text
            news_dict["date"] = dateparser.parse(
                date_p_tag.find("span").text.split("T")[0],settings={'TIMEZONE': 'UTC'}
            ).strftime("%Y-%m-%d")
            news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third website
        try:
            response = requests.get(
                "https://www.echemi.com/cms-news.html",
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
            logging.error(exception_msg)

        # Fourth website
        # Selenium Driver Headless Chrome
        try:
            url = "https://cen.acs.org/"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            post_container = soup.find(
                "div",
                class_="feedburnerFeedBlock",
            )
            for li in post_container.find_all("li", limit=3):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("a").text
                news_dict["Link"] = li.find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("a").text
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        # Selenium Driver Headless Chrome
        try:
            url = "https://www.chemicalprocessing.com/industrynews/"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for li in soup.find_all("li", limit=3, class_="articles-index-list-item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("a").text
                news_link = li.find("a", href=True)
                news_dict["Link"] = "https://www.chemicalprocessing.com" + news_link["href"]
                news_dict["Snippet"] = li.find("h2", class_="deck").text.strip()
                news_dict["date"] = dateparser.parse(
                    li.find("div", class_="date").text.strip(),settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list