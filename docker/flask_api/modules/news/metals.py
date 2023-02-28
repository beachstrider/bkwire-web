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


class MetalsNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.fastmarkets.com/search?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li_tag in soup.find_all("li", limit=5, class_="SearchResultsModule-results-item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("div", class_="PagePromo-title").text.strip()
                news_dict["Link"] = li_tag.find("div", class_="PagePromo-title").find("a", class_="Link", href=True)["href"]
                news_dict["Snippet"] = li_tag.find("div", class_="PagePromo-description").text.strip()
                news_dict["date"] = dateparser.parse(li_tag.find("div", class_="PagePromo-date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            url = "https://www.amm.com/SearchResults.aspx#!?term=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-result-footer")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div_tag in soup.find_all("div", limit=5, class_="search-result ng-scope"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div_tag.find("h2").text.strip()
                news_dict["Link"] = ("https://www.amm.com" + div_tag.find("h2").find("a", href=True)["href"])
                news_dict["Snippet"] = div_tag.find("h2").text.strip()
                news_dict["date"] = dateparser.parse(div_tag.find("div", class_="search-result-footer").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)


        # Third Website
        try:
            response = requests.get(
                "https://www.steelorbis.com/steel-companies/company/companyContactSearch.do?method=showArticleSearchView&searchKey=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            tbody_tag = soup.find("tbody")
            for tr_tag in tbody_tag.find_all("tr", limit=5):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = tr_tag.find_all("td")[0].find("a").text.strip()
                news_dict["Link"] = ("https://www.steelorbis.com" + tr_tag.find_all("td")[0].find("a", href=True)["href"])
                news_dict["Snippet"] = tr_tag.find_all("td")[0].find("a").text.strip()
                news_dict["date"] = dateparser.parse(tr_tag.find_all("td")[2].text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website 
        try:
            response = requests.get(
                "https://americanrecycler.com/8568759/index.php/search?searchword=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            dl_tag = soup.find("dl", class_="search-results")
            for (dt_tag,dd_tag_text,dd_tag_date) in zip(dl_tag.find_all("dt", limit=5, class_="result-title"),
                                                        dl_tag.find_all("dd", limit=5, class_="result-text"),
                                                        dl_tag.find_all("dd", limit=5, class_="result-created")):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = dt_tag.find("a").text.strip()
                news_dict["Link"] = ("https://americanrecycler.com" + dt_tag.find("a", href=True)["href"])
                news_dict["Snippet"] = dd_tag_text.text.strip()
                news_dict["date"] = dateparser.parse(dd_tag_date.text.split("on")[-1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)


        # Fifth Website
        try:
            response = requests.get(
                "https://search.freefind.com/find.html?si=91023682&pid=r&n=0&_charset_=UTF-8&bcd=%C3%B7&query=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
                timeout=5,
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for font_tag in soup.find_all("font", limit=5, class_="search-results"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = font_tag.find("a").text.strip()
                news_dict["Link"] = font_tag.find("a", href=True)["href"]
                news_dict["Snippet"] = font_tag.text.strip().split("https")[0].split("...",1)[1]
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"Privacy Error, Site Can't Open {exception_msg}")

        # Seventh Website
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