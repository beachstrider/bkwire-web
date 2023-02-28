import datetime
import requests
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class GeneralNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website 
        try:
            response = requests.get(
                "https://www.pymnts.com//?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li_tag in soup.find_all("li", limit=3, class_="infinite-post"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("h2").text.strip()
                news_dict["Link"] = li_tag.find("a", href=True)["href"]
                news_dict["Snippet"] = li_tag.find("p").text.strip()
                news_dict["date"] = dateparser.parse(li_tag.find("span", class_="date_search").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://finance.yahoo.com/lookup?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            main_div_tag = soup.find("div", attrs={"id": "Fin-Stream"})
            for div_tag in main_div_tag.find_all(
                "div", limit=3, attrs={"data-test-locator": "mega"}
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div_tag.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://finance.yahoo.com"
                    + div_tag.find("h3").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div_tag.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error("Site not have any bankruptcy news")

        # Third Website
        try:
            url = "https://www.reuters.com/site-search/?query=bankruptcy&offset=0"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div_tag in soup.find_all("div", limit=6, attrs={"data-testid": "MediaStoryCard"}):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div_tag.find("a", attrs={"data-testid": "Heading"}).text.strip()
                news_dict["Link"] = ("https://www.reuters.com" + div_tag.find("a", attrs={"data-testid": "Heading"}, href=True)["href"])
                news_dict["Snippet"] = div_tag.find( "a", attrs={"data-testid": "Heading"} ).text.strip()
                news_dict["date"] = dateparser.parse(div_tag.find("time").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.reuters.com/news/archive/bankruptcyNews",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=3, class_="story"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.reuters.com"
                    + article.find("h3").find_parent("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("time", class_="article-time").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.wsj.com/pro/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=3):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = article.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://www.businessinsider.in/searchresult.cms?query=bankruptcy&sortorder=score",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for (anchor_tag, div_tag, date_div_tag) in zip(
                soup.find_all("a", limit=3, class_="list-title-link"),
                soup.find_all("div", limit=3, class_="list-bottom-text"),
                soup.find_all("div", limit=3, class_="list-timestamp"),
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = anchor_tag.text.strip()
                news_dict["Link"] = anchor_tag["href"]
                news_dict["Snippet"] = div_tag.text.strip()
                news_dict["date"] = dateparser.parse(date_div_tag["data-dateformat"],settings={'TIMEZONE': 'UTC'}).strftime(
                    "%Y-%m-%d"
                )
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list