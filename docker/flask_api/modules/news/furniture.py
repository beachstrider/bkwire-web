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


class FurnitureNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.furniturenews.net/search/site/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="home-page-block article-carousel")
            for li_tag in soup.find_all("li", class_="search-result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.furniturenews.net"
                    + li_tag.find("h3").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li_tag.find(
                    "p", class_="search-snippet"
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    li_tag.find("p", class_="search-info").text.split("-")[1],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.furnituretoday.com/?wpsolr_q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=4, class_="post-item post-item--river"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                news_dict["Link"] = div.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find(
                    "div", class_="post-item__excerpt body-text post-content"
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("p", class_="dateline").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            url = "https://www.furninfo.com/Search/?q=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "gs-title")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all("div", limit=4, class_="gsc-webResult gsc-result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div",class_="gs-title").text.strip()
                news_dict["Link"] = div.find("div",class_="gs-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[1].strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website 
        try:
            url = "http://hfbusiness.com/Search-Results?search=bankruptcy&sort=1"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "dnnSearchResultItem-Title")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            div_tag = soup.find("div",class_="dnnSearchResultContainer")
            for div in div_tag.find_all("div", limit=4, class_="dnnSearchResultItem"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div",class_="dnnSearchResultItem-Title").text.strip()
                news_dict["Link"] = div.find("div",class_="dnnSearchResultItem-Title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="dnnSearchResultItem-Description").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="dnnSearchResultItem-Others").text.split(":")[1],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.furnitureproduction.net/search/site/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="home-page-block article-carousel")
            for article in div_tag.find_all("article", limit=3):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2").text.strip()
                news_dict["Link"] = (
                    "https://www.furnitureproduction.net"
                    + article.find("h2").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find(
                    "span", class_="article-summary"
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("span", class_="article-meta").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error("Site not have any bankruptcy news")

        return news_list