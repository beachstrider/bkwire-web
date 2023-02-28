import requests
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper


class PaperAndPackagingNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.packaginginsights.com/Searchresult.html?bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div",class_="left-content")
            for div in div_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="subtitle").text.strip()
                news_dict["Link"] = div.find("div", class_="subtitle").find("a", href=True)["href"]
                news_dict["Snippet"] = (div.find("div", class_="news-row-content").text.split("...")[0].strip())
                news_dict["date"] = dateparser.parse(div.find("div", class_="summary_style").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.packagingdigest.com/search/node/bankruptcy?sort=field_penton_published_datetime&order=desc",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=4):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("div", class_="title").text.strip()
                news_dict["Link"] = ("https://www.packagingdigest.com" + article.find("div", class_="title").find("a", href=True)["href"])
                news_dict["Snippet"] = article.find("div", class_="summary").text.strip()
                news_dict["date"] = dateparser.parse(article.find("span", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.packagingstrategies.com/search?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("div", limit=3, class_="record"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2").find("a").text.strip()
                news_dict["Link"] = article.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("div",class_="abstract").text.strip()
                news_dict["date"] = dateparser.parse(article.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.paperandpackaging.org/search/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="views-row"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3", class_="node-title").text.strip()
                news_dict["Link"] = ("https://www.paperandpackaging.org" + div.find("a", href=True, class_="media-pdf-link")["href"])
                news_dict["Snippet"] = div.find("h3", class_="node-title").text.strip()
                news_dict["date"] = dateparser.parse(div.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.packworld.com/search?searchQuery=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div",class_="node-list__nodes")
            for div in div_tag.find_all("div", limit=3, class_="node-list__node"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h5").text.strip()
                news_dict["Link"] = ("https://www.packworld.com" + div.find("h5").find("a", href=True)["href"])
                news_dict["Snippet"] = div.find("div", class_="section-feed-content-node__content-teaser").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="section-feed-content-node__content-published").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://www.flexpackmag.com/search?q=bankruptcy&sort=date",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("div", limit=3, class_="record"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2").find("a").text.strip()
                news_dict["Link"] = article.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("div",class_="abstract").text.strip()
                news_dict["date"] = dateparser.parse(article.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.packagingtechtoday.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="pp-content-grid-post-text"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = div.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="post-date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list
