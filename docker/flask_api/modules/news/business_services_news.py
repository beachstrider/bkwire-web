import datetime
import requests
import logging
from bs4 import BeautifulSoup
import dateparser
from .base import NewsScraper


class BusinessServicesNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://staffinghub.com/category/news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="td_module_14 td_module_wrap td-animation-stack"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3", class_="entry-title td-module-title").text.strip()
                news_dict["Link"] = div.find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="td-excerpt").text.strip().split("...\r\n")[0]
                news_dict["date"] = dateparser.parse(div.find("time", class_="entry-date updated td-module-date")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://americanstaffing.net/staffing-industry-news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="active tab-pane")
            for li in div_tag.find_all("li", limit=2, class_="asa-feed-item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("div", class_="page-title").text.strip()
                news_dict["Link"] = li.find("a", href=True, class_="text")["href"]
                news_dict["Snippet"] = li.find("div", class_="page-title").text.strip()
                news_dict["date"] = dateparser.parse(li.find("span", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third website
        try:
            response = requests.get(
                "https://www.accountingtoday.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="PromoLargeImageRight-content")
            news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
            news_dict["Title"] = div_tag.find("div", class_="PromoLargeImageRight-title").text.strip()
            news_dict["Snippet"] = div_tag.find("p").text.strip()
            news_dict["date"] = dateparser.parse(div_tag.find("div", class_="PromoLargeImageRight-timeSince").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
            news_link_div_tag = div_tag.find("div", class_="PromoLargeImageRight-title")
            news_dict["Link"] = news_link_div_tag.find("a", href=True)["href"]

            news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth website
        try:
            response = requests.get(
                "https://www.journalofaccountancy.com/news.html",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h1").text.strip()
                news_dict["Link"] = ("https://www.journalofaccountancy.com" + article.find("a", href=True)["href"])
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = dateparser.parse(article.find("div", class_="date-time")["data-time"].split("T")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth website
        try:
            response = requests.get(
                "https://www.cpajournal.com/category/magazine/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = article.find("a", href=True)["href"]
                snippet_div_tag = article.find("div", class_="newsmag-content entry-content")
                news_dict["Snippet"] = snippet_div_tag.find("p").text.strip()
                news_dict["date"] = dateparser.parse(article.find("div", class_="meta").text.splitlines()[-2],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth website
        try:
            response = requests.get(
                "https://www.fm-magazine.com/news.html",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", class_="resource-list-item", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.fm-magazine.com" + article.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find(
                    "p", class_="resource-list-item__description"
                ).text.strip()
                news_dict["date"] = dateparser.parse(article.find("span", class_="resource-list-item__date formatted-date")["data-date"].split("T")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh website
        try:
            response = requests.get(
                "https://www.thesoftwarereport.com/category/latest-news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", class_="td-meta-info-container", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find(
                    "h3", class_="entry-title td-module-title"
                ).text.strip()
                news_dict["Snippet"] = div.find(
                    "h3", class_="entry-title td-module-title"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_dict["Link"] = div.find("a", href=True, attrs={"rel": "bookmark"})[
                    "href"
                ]
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eighth website
        try:
            response = requests.get(
                "https://www.natlawreview.com/Latest-Legal-News-Analysis",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_content = soup.find("div", class_="view-content")

            for (td, day_div, month_div) in zip(
                div_content.find_all("td", class_="views-field views-field-title", limit=3),
                div_content.find_all("div", class_="day", limit=3),
                div_content.find_all("div", class_="month", limit=3),
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = td.find("a").text.strip()
                news_dict["Link"] = td.find("a", href=True)["href"]
                news_dict["Snippet"] = td.find("a").text.strip()
                news_dict["date"] = dateparser.parse(day_div.text + " " + month_div.text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Nineth website
        try:
            response = requests.get(
                "https://www.law360.com/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", class_="hnews hentry", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.law360.com" + li.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li.find("p").text.strip()
                news_dict["date"] = dateparser.parse(li.find("span")["title"],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list
