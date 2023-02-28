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


class ApparelNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://apparelresources.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="grid-header-box"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="grid-title entry-title").text
                news_dict["Link"] = div.find("h2", class_="grid-title entry-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("h2", class_="grid-title entry-title").text
                news_dict["date"] = dateparser.parse(div.find("time").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website 
        try:
            response = requests.get(
                "https://www.just-style.com/s/?wpsolr_q=bankruptcy&wpsolr_sort=sort_by_date_desc",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all(
                "article", limit=2, class_="c-story c-story--catalogue"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = article.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("p", class_="c-story__header__subtitle").text.strip()
                news_dict["date"] = dateparser.parse(article.find("span",class_="pdate").text.split("|")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "http://www.textilesinthenews.org/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2").text.strip()
                news_dict["Link"] = article.find("h2").find("a", href=True)["href"]
                try:
                    news_dict["Snippet"] = article.find("div",class_="entry-content").text.strip()
                except:
                    news_dict["Snippet"] = article.find("h2").text.strip()
                news_dict["date"] = dateparser.parse(article.find("time").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # fourth website
        try:
            response = requests.get(
                "https://www.apparelnews.net/search/?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", class_="item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h4").text.strip()
                news_dict["Link"] = (
                    "https://www.apparelnews.net"
                    + div.find("a", href=True, class_=None)["href"]
                )
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(div.find_all("li")[-1].text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # fifth website
        try:
            url = "https://wwd.com/search/#?q=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "text-block")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all(
                "div",
                limit=2,
                class_="result block",
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="result-title").text.strip()
                news_dict["Link"] = div.find("div", class_="result-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="text-block").text.strip()
                news_dict["date"] = dateparser.parse(div.find_all("span")[1].text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # sixth website
        try:
            response = requests.get(
                "https://fashionista.com/search?query=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=1, class_="l-grid--item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                phoenix_ellipsis = div.find(
                    "phoenix-ellipsis", class_="m-ellipsis m-card--header"
                )
                news_dict["Link"] = (
                    "https://fashionista.com"
                    + phoenix_ellipsis.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # seventh website
        try:
            response = requests.get(
                "https://fashionweekdaily.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=4, class_="list-post pclist-layout"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h2").text.strip()
                h2_tag = li.find("h2", class_="penci-entry-title entry-title grid-title")
                news_dict["Link"] = h2_tag.find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("p").text.strip()
                news_dict["date"] = dateparser.parse(li.find("time", class_="entry-date published").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")  

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # eighth website
        try:
            url = "https://www.cnbc.com/search/?query=Apparel%20bankruptcy&qsearchterm=Apparel%20bankruptcy"
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
            for div in div_tag.find_all("div", limit=2, class_="SearchResult-searchResultContent"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a", class_="resultlink").text.strip()
                news_dict["Link"] = div.find("a", href=True, class_="resultlink")["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span", class_="SearchResult-publishedDate").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # nineth website
        try:
            response = requests.get(
                "https://www.fibre2fashion.com/news/allnews.aspx?category=news&IsAutoSuggest=0&keywords=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=3, class_="latest-news-box"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="blocktitle").text.strip()
                news_dict["Link"] = div.find("div", class_="blocktitle").find("a", href=True)["href"]
                date_list = div.find("span", class_="news-date").text.split(" ")[1:]
                news_dict["date"] = dateparser.parse(" ".join(date_list),settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_dict["Snippet"] = div.find("div", class_="blocktitle").text.strip()

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list
