import requests
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper


class FurnitureNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.furniturenews.net/",
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
                    "https://www.furniturenews.net"
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
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.furnituretoday.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=3, class_="post-item post-item--river"):
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
            response = requests.get(
                "https://www.furninfo.com/furniture-industry-news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="col-lg-12")
            for div in div_tag.find_all("div", limit=3):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a", class_="link-success").text.strip()
                news_dict["Link"] = (
                    "https://www.furninfo.com/furniture-industry-news/"
                    + div.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find(
                    "span", attrs={"itemprop": "description"}
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("span", attrs={"itemprop": "datePublished"}).text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "http://hfbusiness.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="lawidget recent-articles")
            for div in div_tag.find_all("div", limit=3, class_="item-article"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h5").text.strip()
                news_dict["Link"] = div.find("h5").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p", class_="laFont").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("p", class_="post-meta").text.split("\n")[1],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.furnitureproduction.net/news",
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
            logging.error(exception_msg)

        return news_list