import datetime
import requests
import logging
from bs4 import BeautifulSoup
import dateparser
from .base import NewsScraper


class ConstructionNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://aec-business.com/",
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
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.builderonline.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for figcaption in soup.find_all(
                "figcaption", limit=2, class_="m-tagged-promos-lead__text"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = figcaption.find(
                    "a", href=True, class_="f4 title lh-large altLink db pb1 b--builder"
                ).text.strip()
                news_dict["Link"] = figcaption.find(
                    "a", href=True, class_="f4 title lh-large altLink db pb1 b--builder"
                )["href"]
                news_dict["Snippet"] = figcaption.find(
                    "span", class_="dn db-ns serif--builder f5 f6--ar lh-copy pb1"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.bdcnetwork.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for h3 in soup.find_all(
                "h3", limit=2, class_="views-field views-field-title prose"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = h3.find("span", class_="field-content").text.strip()
                news_dict["Link"] = (
                    "https://www.bdcnetwork.com" + h3.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = h3.find("span", class_="field-content").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.constructconnect.com/blog",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="bop--listing--item block"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                news_dict["Link"] = div.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = (
                    div.find("div", class_="bop--listing--item--body")
                    .find("p")
                    .text.strip()
                )
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="post-item--published").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.constructiondive.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.constructiondive.com"
                    + li.find("h3").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li.find("p", class_="feed__description").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://construction-today.com/news/category/news/",
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
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.equipmentworld.com/business",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="section-feed-content-node__contents"
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

        # eighth website
        try:
            response = requests.get(
                "https://www.cnbc.com/construction/",
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

        # Nineth Website
        try:
            response = requests.get(
                "https://www.timberindustrynews.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="list-item cf"):
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

