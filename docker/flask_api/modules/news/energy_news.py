import datetime
import requests
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper


class OilAndGasNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://oilprice.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="breakingNewsBlock")
            for anchor_tag in div_tag.find_all(
                "a", limit=2, class_="breakingNewsBlock__article"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = anchor_tag.find(
                    "h3", class_="breakingNewsBlock__articleTitle"
                ).text.strip()
                news_dict["Link"] = anchor_tag["href"]
                news_dict["Snippet"] = anchor_tag.find(
                    "h3", class_="breakingNewsBlock__articleTitle"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.oilandgas360.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", attrs={"id": "slidemain"})
            for li_tag in div_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("h2").text.strip()
                news_dict["Link"] = li_tag.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = " ".join([p.text for p in li_tag.find_all("p")])
                news_dict["date"] = dateparser.parse(
                    li_tag.find("div", class_="featured-meta").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.ogj.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="item small"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.ogj.com"
                    + div.find("h3").find_parent("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("h3").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # fourth Website
        try:
            response = requests.get(
                "https://www.rigzone.com/news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="headlineContainer"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a").text.strip()
                news_dict["Link"] = (
                    "https://www.rigzone.com" + div.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("div", class_="description").text.split(
                    div.find("span", class_="date").text
                )[-1]
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.worldoil.com/news",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="article"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a").text.strip()
                news_dict["Link"] = (
                    "https://www.worldoil.com" + div.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("a").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="news-date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://www.upstreamonline.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="card-body"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                news_dict["Link"] = (
                    "https://www.upstreamonline.com"
                    + div.find("h2").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("h2").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.solarpowerworldonline.com/category/industry-news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2", class_="entry-title").text.strip()
                news_dict["Link"] = article.find("h2", class_="entry-title").find(
                    "a", href=True
                )["href"]
                news_dict["Snippet"] = article.find("h2", class_="entry-title").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("time", class_="entry-time").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eighth Website
        try:
            response = requests.get(
                "https://energynews.us/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="entry-wrapper"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="entry-title").text.strip()
                news_dict["Link"] = div.find("h2", class_="entry-title").find(
                    "a", href=True
                )["href"]
                news_dict["Snippet"] = div.find("h2", class_="entry-title").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("time", class_="entry-date published")["datetime"].split("T")[
                        0
                    ],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list
