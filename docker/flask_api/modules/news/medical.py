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


class MedicalNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.medicalnews.md/?s=bankruptcy&submit=Search",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", attrs={"id":"primary"})
            for article in div_tag.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h1",class_="entry-title").text.strip()
                news_dict["Link"] = article.find("h1",class_="entry-title").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("div",class_="entry-content").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            url = "https://search.medscape.com/search/?q=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            try:
                WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "searchResultTitle")))
            except:
                pass
            soup = BeautifulSoup(driver.page_source, "html.parser")
            div_tag = soup.find("div", attrs={"id":"allSearchResults"})
            for div in div_tag.find_all("div", limit=4, class_="searchResult"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("p", class_="searchResultTitle").text.strip()
                news_dict["Link"] = "https:" + div.find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="searchResultTeaser").text.strip()
                news_dict["date"] = dateparser.parse(div.find("p", class_="searchResultSources").text.split(",",1)[1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://nutraceuticalbusinessreview.com/search?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div",  class_="pt-1 pb-3 dotted-bottom-border"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a").text.strip()
                news_dict["Link"] = ("https://nutraceuticalbusinessreview.com" + div.find("a", href=True)["href"])
                news_dict["Snippet"] = div.find("a").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="d-inline-block ms-2").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.nutraceuticalsworld.com/contents/searchcontent/2647/bankruptcy/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="media-body"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h4").text.strip()
                news_dict["Link"] = ("https://www.nutraceuticalsworld.com" + div.find("h4").find("a", href=True)["href"])
                if div.find("div", class_="li16").text.strip() == "...":
                    news_dict["Snippet"] = div.find("h4").text.strip()
                else:
                    news_dict["Snippet"] = div.find("div", class_="li16").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.biopharmadive.com/search/?q=bankruptcy&selected_facets=section_exact%3Anews&topics=&sortby=on",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li_tag in soup.find_all("li", limit=5, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("h3").text.strip()
                news_dict["Link"] = "https://www.biopharmadive.com" + li_tag.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = li_tag.find("h3").text.strip()
                news_dict["date"] = dateparser.parse(li_tag.find_all("span",class_="secondary-label")[1].text.split(":")[1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            url = "https://www.cnbc.com/search/?query=Medical%20bankruptcy"
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
            for div in div_tag.find_all("div", limit=5, class_="SearchResult-searchResultContent"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a", class_="resultlink").text.strip()
                news_dict["Link"] = div.find("a", href=True, class_="resultlink")["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span", class_="SearchResult-publishedDate").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website medical
        try:
            response = requests.get(
                "https://www.worldpharmanews.com/search?searchword=bankruptcy&searchphrase=all",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            dl_tag = soup.find("dl", class_="search-results")
            for (dt_tag,dd_tag_text,dd_tag_date) in zip(dl_tag.find_all("dt", class_="result-title"),
                                                        dl_tag.find_all("dd", class_="result-text"),
                                                        dl_tag.find_all("dd", class_="result-created")):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = dt_tag.find("a").text.strip()
                news_dict["Link"] = ("https://americanrecycler.com" + dt_tag.find("a", href=True)["href"])
                news_dict["Snippet"] = dd_tag_text.text.strip()
                news_dict["date"] = dateparser.parse(dd_tag_date.text.split("on")[-1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list