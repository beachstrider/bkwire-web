import datetime
import requests
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper


class GeneralNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.pymnts.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="blog-widget-wrap left relative")
            for li_tag in div_tag.find_all("li", limit=3):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("h2").text.strip()
                news_dict["Link"] = li_tag.find("a", href=True)["href"]
                news_dict["Snippet"] = li_tag.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://finance.yahoo.com/news",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            main_div_tag = soup.find("div", attrs={"id": "Fin-Stream"})
            for div_tag in main_div_tag.find_all(
                "div", limit=3, attrs={"data-test-locator": "mega"}
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div_tag.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://finance.yahoo.com"
                    + div_tag.find("h3").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div_tag.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.reuters.com/business/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div_tag in soup.find_all(
                "div", limit=3, attrs={"data-testid": "MediaStoryCard"}
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div_tag.find(
                    "a", attrs={"data-testid": "Heading"}
                ).text.strip()
                news_dict["Link"] = (
                    "https://www.reuters.com"
                    + div_tag.find("a", attrs={"data-testid": "Heading"}, href=True)["href"]
                )
                news_dict["Snippet"] = div_tag.find(
                    "a", attrs={"data-testid": "Heading"}
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.reuters.com/business/finance/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div_tag in soup.find_all(
                "div", limit=3, attrs={"data-testid": "MediaStoryCard"}
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div_tag.find(
                    "a", attrs={"data-testid": "Heading"}
                ).text.strip()
                news_dict["Link"] = (
                    "https://www.reuters.com"
                    + div_tag.find("a", attrs={"data-testid": "Heading"}, href=True)["href"]
                )
                news_dict["Snippet"] = div_tag.find(
                    "a", attrs={"data-testid": "Heading"}
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.reuters.com/news/archive/bankruptcyNews",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=3, class_="story"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.reuters.com"
                    + article.find("h3").find_parent("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("time", class_="article-time").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://www.wsj.com/pro/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=3):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = article.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.businessinsider.com/retail",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for (anchor_tag, div_tag, date_div_tag) in zip(
                soup.find_all("a", limit=3, class_="list-title-link"),
                soup.find_all("div", limit=3, class_="list-top-text"),
                soup.find_all("div", limit=3, class_="list-timestamp"),
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = anchor_tag.text.strip()
                news_dict["Link"] = anchor_tag["href"]
                news_dict["Snippet"] = div_tag.text.strip()
                news_dict["date"] = dateparser.parse(date_div_tag["data-dateformat"],settings={'TIMEZONE': 'UTC'}).strftime(
                    "%Y-%m-%d"
                )
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eighth Website
        try:
            response = requests.get(
                "https://wolfstreet.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=3):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h1", class_="entry-title").text.strip()
                news_dict["Link"] = article.find("h1", class_="entry-title").find(
                    "a", href=True
                )["href"]
                news_dict["Snippet"] = article.find("div", class_="excerpt").text.strip()
                news_dict["date"] = dateparser.parse(article.find("time")["datetime"],settings={'TIMEZONE': 'UTC'}).strftime(
                    "%Y-%m-%d"
                )
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list
