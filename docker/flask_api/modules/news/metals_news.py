import datetime
import requests
import time
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class MetalsNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.fastmarkets.com/metals-and-mining/steel-and-steel-raw-materials",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="PageListP-items-item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="PagePromo-title").text.strip()
                news_dict["Link"] = div.find("a", class_="Link", href=True)["href"]
                news_dict["Snippet"] = div.find(
                    "div", class_="PagePromo-title"
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="PagePromo-date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            url = "https://www.amm.com/News/Steel.html"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            ul_tag = soup.find("ul", class_="article_list")
            for li in ul_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("a").text.strip()
                news_dict["Link"] = (
                    "https://www.amm.com" + li.find("a", href=True)["href"].split("..")[1]
                )
                news_dict["Snippet"] = li.find("a").text.strip()
                news_dict["date"] = dateparser.parse(
                    li.find("span", class_="date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            url = "https://www.steelbb.spglobal.com/lateststeelnews/"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
            news_dict["Title"] = (
                soup.find("td", class_="alist_title_td").find("a").text.strip()
            )
            news_dict["Link"] = (
                "https://www.steelbb.spglobal.com"
                + soup.find("td", class_="alist_title_td").find("a")["href"]
            )
            news_dict["Snippet"] = (
                soup.find("td", class_="alist_title_td").find("a").text.strip()
            )
            news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
            news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.steelorbis.com/steel-news/latest-news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=4, class_="col-sm-12 article-shell"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.text.split("\t\t")[-1].strip()
                news_dict["Link"] = (
                    "https://www.steelorbis.com" + div.find_parent("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.text.split("\t\t")[-1].strip()
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="article-date-body").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://americanrecycler.com/8568759/index.php",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find_all("div", class_="slider-container")[1]
            for li in div_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("div", class_="slide-title").text.strip()
                news_dict["Link"] = (
                    "https://americanrecycler.com"
                    + li.find("div", class_="slide-title").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li.find("div", class_="slide-title").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://eng.snmnews.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="auto-article")
            for li in div_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("a").text.strip()
                news_dict["Link"] = (
                    "https://eng.snmnews.com" + li.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.steelonthenet.com/news.php",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
                timeout=5,
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", attrs={"id": "trim"})
            for (a_tag, em_tag) in zip(
                div_tag.find_all("a", limit=2),
                div_tag.find_all("em", limit=2),
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = a_tag.text.strip()
                news_dict["Link"] = a_tag["href"]
                news_dict["Snippet"] = a_tag.text.strip()
                news_dict["date"] = dateparser.parse(em_tag.text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"Privacy Error, Site Can't Open {exception_msg}")

        # Eighth Website
        try:
            url = "https://twitter.com/steel_news?lang=en"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for article in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = (
                    article.find("div", attrs={"data-testid": "tweetText"})
                    .find("span")
                    .text.strip()
                )
                news_dict["Link"] = article.find(
                    "div", attrs={"data-testid": "tweetText"}
                ).find("a")["href"]
                news_dict["Snippet"] = (
                    article.find("div", attrs={"data-testid": "tweetText"})
                    .find("span")
                    .text.strip()
                )
                news_dict["date"] = dateparser.parse(
                    article.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"Site have lazy loading proccess {exception_msg}")


        return news_list

