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


class FinancialServicesNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.abladvisor.com/SearchMain.aspx?text=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="landingList"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="title").find("a").text.strip()
                news_dict["Link"] = div.find("div", class_="title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="desc").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.monitordaily.com/?s=bankruptcy&post_type=post%2Cpage%2Cevent%2Cnews_entry%2Ce_news_entry%2Carticle%2Copinion%2Cservice-directory",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="post-full col-sm-12"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3", class_="post-title-full").text.strip()
                news_dict["Link"] = div.find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p").text.split("read more")[0].strip()
                news_dict["date"] = dateparser.parse(
                    div.find("p", class_="post-date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.pymnts.com//?s=Financial+Services+bankruptcy",
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

        # Fourth Website
        try:
            url = "https://www.cnbc.com/search/?query=Financial%20Services%20bankruptcy&qsearchterm=Financial%20Services%20bankruptcy"
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

        # Fifth Website
        try:
            response = requests.get(
                "https://pitchbook.com/news/search?query=bankruptcy&refType=NA",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for a_tag in soup.find_all("a", limit=2, class_="XL-12 link-wrap d-inline-block"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = a_tag.find("h3").text.strip()
                news_dict["Link"] = "https://pitchbook.com" + a_tag["href"]
                news_dict["Snippet"] = a_tag.find("p",class_="mb-xl-0 text-ellipsis-XL-3").text.strip()
                news_dict["date"] = dateparser.parse(a_tag.find("p", class_="text-small mb-xl-15").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://www.bankingdive.com/search/?q=bankruptcy&selected_facets=&topics=&sortby=on",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3", class_="feed__title").text.strip()
                news_dict["Link"] = ("https://www.bankingdive.com"+ li.find("h3").find("a", href=True)["href"])
                news_dict["Snippet"] = li.find("h3", class_="feed__title").text.strip()
                news_dict["date"] = dateparser.parse(li.find_all("span")[-1].text.split(":")[-1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        

        # Seventh Website
        try:
            response = requests.get(
                "https://bankingjournal.aba.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="row listing")
            for article in div_tag.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2", attrs={"itemprop":"name"}).text.strip()
                news_dict["Link"] = article.find("h2", attrs={"itemprop":"name"}).find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("div",class_="excerpt").text.strip()
                news_dict["date"] = dateparser.parse(article.find("time").text.split("T")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eighth Website 
        try:
            response = requests.get(
                "https://www.americanbanker.com/search?q=bankruptcy#nt=navsearch",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=1, class_="PromoMediumImageLeft-content"):
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

        # Ninth Website
        try:
            url = "https://commercialobserver.com/?s=bankruptcy"
            options = Options()
            options.headless = True
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all("div", limit=1, class_="medium-card card"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = div.find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("h3").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Tenth Website
        try:
            url = "https://www.privateequityinternational.com/?s=bankruptcy"
            options = Options()
            options.headless = True
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="td_module_16 td_module_wrap td-animation-stack"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find(
                    "h3", class_="entry-title td-module-title"
                ).text.strip()
                news_dict["Link"] = div.find(
                    "h3", class_="entry-title td-module-title"
                ).find("a", href=True)["href"]
                news_dict["Snippet"] = div.find(
                    "div", class_="td-excerpt"
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eleventh Website
        url = "https://www.businessinsurance.com/section/search?q=bankruptcy"
        options = Options()
        options.headless = True
        driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
        driver.get(url)
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "overline")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            ul_tag = soup.find("ul", class_="searchlist")
            for li in ul_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3").text.strip()
                news_dict["Link"] = li.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("p").text.strip()
                news_dict["date"] = dateparser.parse(li.find("span",class_="overline").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"Site have lazy loading proccess {exception_msg}")

        return news_list