import datetime
import requests
import time
import logging
from bs4 import BeautifulSoup
import dateparser
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class FinancialServicesNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.abladvisor.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="newsContent"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="text").find("a").text.strip()
                news_dict["Link"] = div.find("div", class_="text").find("a", href=True)[
                    "href"
                ]
                news_dict["Snippet"] = div.find("span", class_="desc").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="time").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.monitordaily.com/news-posts/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="col-sm-9"):
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
                "https://magazine.factoring.org/news",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for section in soup.find_all("section", limit=2, class_="blog-item-summary"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = section.find("h1", class_="blog-title").text.strip()
                news_dict["Link"] = (
                    "https://magazine.factoring.org"
                    + section.find("h1", class_="blog-title").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = section.find("h1", class_="blog-title").text.strip()
                news_dict["date"] = dateparser.parse(
                    section.find("time", class_="blog-date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.pymnts.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="blog-widget-wrap left relative")
            for li in div_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h2").text.strip()
                news_dict["Link"] = li.find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.cnbc.com/commercial-real-estate/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div = soup.find("div", class_="Layout-layout")
            for div in div.find_all("div", limit=2, class_="Card-textContent"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a", class_="Card-title").text.strip()
                news_dict["Link"] = div.find("a", href=True, class_="Card-title")["href"]
                news_dict["Snippet"] = div.find("a", class_="Card-title").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="Card-time").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://pitchbook.com/news",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for a_tag in soup.find_all(
                "a", limit=2, class_="XL-12 link-wrap d-inline-block"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = a_tag.find(
                    "h3", class_="font-color-white mb-m-20"
                ).text.strip()
                news_dict["Link"] = "https://pitchbook.com" + a_tag["href"]
                news_dict["Snippet"] = a_tag.find(
                    "h3", class_="font-color-white mb-m-20"
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    a_tag.find("p", class_="font-color-white mb-xl-0").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.bankingdive.com/topic/commercial/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find(
                    "h3", class_="feed__title feed__title--display"
                ).text.strip()
                news_dict["Link"] = (
                    "https://www.bankingdive.com"
                    + li.find("h3").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li.find("p", class_="feed__description").text.strip()
                news_dict["date"] = dateparser.parse(li.find_all("span")[-1].text,settings={'TIMEZONE': 'UTC'}).strftime(
                    "%Y-%m-%d"
                )
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eight Website
        try:
            response = requests.get(
                "https://www.insurancebusinessmag.com/us/tools/tags/commercial-insurance/15831/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="article_content"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3", class_="article_heading").text.strip()
                news_dict["Link"] = (
                    "https://www.insurancebusinessmag.com"
                    + div.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Nineth Website
        try:
            response = requests.get(
                "https://bankingjournal.aba.com/category/commerciallending/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="posts-list list-timeline")
            for article in div_tag.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("a").text.strip()
                news_dict["Link"] = article.find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("a").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("time").text.split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Tenth Website
        try:
            response = requests.get(
                "https://www.americanbanker.com/tag/small-business-banking",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="PromoMediumImageRight-content"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find(
                    "div", class_="PromoMediumImageRight-title"
                ).text.strip()
                news_dict["Link"] = div.find(
                    "div", class_="PromoMediumImageRight-title"
                ).find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                try:
                    news_dict["date"] = dateparser.parse(
                        div.find("div", class_="PromoMediumImageRight-timeSince").text,settings={'TIMEZONE': 'UTC'}
                    ).strftime("%Y-%m-%d")
                except:
                    news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)
        
        # Eleventh Website
        try:
            response = requests.get(
                "https://www.americanbanker.com/tag/commercial-banking",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="PromoMediumImageRight-content"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find(
                    "div", class_="PromoMediumImageRight-title"
                ).text.strip()
                news_dict["Link"] = div.find(
                    "div", class_="PromoMediumImageRight-title"
                ).find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Ninth Website
        try:
            url = "https://commercialobserver.com/finance/"
            options = Options()
            options.headless = True
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all("div", limit=2, class_="medium-card card"):
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
            url = "https://www.privateequityinternational.com/"
            options = Options()
            options.headless = True
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="td_module_2 td_module_wrap td-animation-stack"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find(
                    "h3", class_="entry-title td-module-title"
                ).text.strip()
                news_dict["Link"] = div.find(
                    "h3", class_="entry-title td-module-title"
                ).find("a", href=True)["href"]
                news_dict["Snippet"] = div.find(
                    "h3", class_="entry-title td-module-title"
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eleventh Website
        url = "https://www.businessinsurance.com/"
        options = Options()
        options.headless = True
        driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            ul_tag = soup.find("ul", class_="cmnlist")
            for li in ul_tag.find_all("li", limit=2, class_="article"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3").text.strip()
                news_dict["Link"] = li.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"Site have lazy loading proccess {exception_msg}")

        return news_list
