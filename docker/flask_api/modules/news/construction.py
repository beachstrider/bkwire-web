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


class ConstructionNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://aec-business.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="qubely-post-grid-content"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find(
                    "h2", class_="qubely-postgrid-title"
                ).text.strip()
                news_dict["Snippet"] = div.find(
                    "h2", class_="qubely-postgrid-title"
                ).text.strip()
                news_dict["Link"] = div.find("h2", class_="qubely-postgrid-title").find(
                    "a", href=True
                )["href"]
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error("Oops, the article couldn't be found!")

        # Second Website
        try:
            response = requests.get(
                "https://www.builderonline.com/search?q=bankruptcy&s=newest",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="result-text-wrap"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a").text.strip()
                news_dict["Link"] = div.find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p", class_="blurb").text.strip()
                news_dict["date"] = dateparser.parse(div.find("time").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.bdcnetwork.com/search/all?search_api_fulltext=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=1, class_="postWrap"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h4").text.strip()
                news_dict["Link"] = ("https://www.bdcnetwork.com" + div.find("h4").find("a", href=True)["href"])
                try:
                    news_dict["Snippet"] = div.find("p").text.strip()
                except:
                    news_dict["Snippet"] = div.find("h4").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        

        # Fourth Website
        try:
            response = requests.get(
                "https://www.constructiondive.com/search/?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=4, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3", class_="feed__title").text.strip()
                news_dict["Link"] = ("https://www.constructiondive.com"+ li.find("h3").find("a", href=True)["href"])
                news_dict["Snippet"] = li.find("h3", class_="feed__title").text.strip()
                news_dict["date"] = dateparser.parse(li.find_all("span")[-1].text.split(":")[-1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://construction-today.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="col xs12 sm7 md8"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                news_dict["Link"] = div.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p", class_="exerpt").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error("No search results available for the bankruptcy criteria.")

        # Sixth Website
        try:
            response = requests.get(
                "https://www.equipmentworld.com/search?searchQuery=bankruptcy&sortField=PUBLISHED",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=4, class_="section-feed-content-node__contents"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h5").text.strip()
                news_dict["Link"] = (
                    "https://www.equipmentworld.com"
                    + div.find("h5").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = (
                    div.find("div", class_="section-feed-content-node__content-teaser")
                    .find("a")
                    .text.strip()
                )
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="section-feed-content-node__content-published").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh website
        try:
            url = "https://www.cnbc.com/search/?query=Construction%20bankruptcy&qsearchterm=Construction%20bankruptcy"
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
            for div in div_tag.find_all("div", limit=3, class_="SearchResult-searchResultContent"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a", class_="resultlink").text.strip()
                news_dict["Link"] = div.find("a", href=True, class_="resultlink")["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span", class_="SearchResult-publishedDate").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Nineth Website
        try:
            response = requests.get(
                "https://www.timberindustrynews.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=4, class_="list-item cf"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="list-item__title").text.strip()
                news_dict["Link"] = div.find(
                    "a", href=True, class_="list-item__title-link"
                )["href"]
                news_dict["Snippet"] = div.find(
                    "div", class_="list-item__text"
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="list-item__date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list