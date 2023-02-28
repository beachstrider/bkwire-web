import datetime
import requests
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper


class ApparelNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "http://apparelresources.com/business-news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="content-list-right"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="entry-title grid-title").text
                news_dict["Link"] = div.find("a", class_=None, href=True)["href"]
                news_dict["date"] = dateparser.parse(div.find("time", class_="entry-date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_dict["Snippet"] = div.find("p").text

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.just-style.com/sector/finance/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all(
                "article", limit=2, class_="c-story c-story--catalogue"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find(
                    "h4",
                    class_="post-title c-story__header__headline--catalogue the-global-title",
                ).text.strip()
                h4 = article.find("h4")
                news_dict["Link"] = h4.find("a", href=True)["href"]
                news_dict["Snippet"] = article.find(
                    "p", class_="subtitle subtitle--three"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "http://www.textilesinthenews.org/textile-in-the-news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="news-block"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                h3 = div.find("h3")
                news_dict["Link"] = h3.find("a", href=True)["href"]
                try:
                    news_dict["Snippet"] = div.find("p").text.strip()
                except:
                    news_dict["Snippet"] = div.find("h3").text.strip()
                date_list = div.find("em").text.split(" ")[1:]
                news_dict["date"] = dateparser.parse(" ".join(date_list),settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # fourth website
        try:
            response = requests.get(
                "https://www.apparelnews.net/news/finance/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div = soup.find("div", class_="item")
            news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
            news_dict["Title"] = div.find("h4").text.strip()
            news_dict["Link"] = (
                "https://www.apparelnews.net"
                + div.find("a", href=True, class_=None)["href"]
            )
            news_dict["Snippet"] = div.find("p").text.strip()
            news_dict["date"] = dateparser.parse(div.find("li").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
            news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # fifth website
        try:
            response = requests.get(
                "https://wwd.com/business-news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div",
                limit=2,
                class_="story // lrv-u-padding-t-1 lrv-u-padding-b-150 lrv-u-padding-tb-2@desktop lrv-u-display-inline-block lrv-u-width-100p",
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                h3 = div.find("h3")
                news_dict["Link"] = h3.find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(div.find("time").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # sixth website
        try:
            response = requests.get(
                "https://fashionista.com/business",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="l-grid--item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                phoenix_ellipsis = div.find(
                    "phoenix-ellipsis", class_="m-ellipsis m-card--header"
                )
                news_dict["Link"] = (
                    "https://fashionista.com"
                    + phoenix_ellipsis.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # seventh website
        try:
            response = requests.get(
                "https://fashionweekdaily.com/category/news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="list-post pclist-layout"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h2").text.strip()
                h2_tag = li.find("h2", class_="penci-entry-title entry-title grid-title")
                news_dict["Link"] = h2_tag.find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("p").text.strip()
                news_dict["date"] = dateparser.parse(li.find("time", class_="entry-date published").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")  

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # eighth website
        try:
            response = requests.get(
                "https://www.cnbc.com/apparel/",
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
                news_dict["date"] = dateparser.parse(div.find("span", class_="Card-time").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # nineth website
        try:
            response = requests.get(
                "https://www.fibre2fashion.com/news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=3, class_="col-sm-4 col-xs-4 must-read-detailsblock"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h5", class_="blue-subheading").text.strip()
                news_dict["Link"] = div.find("a", href=True)["href"]
                date_list = div.find("span", class_="news-top-smalltxt").text.split(" ")[2:]
                news_dict["date"] = dateparser.parse(" ".join(date_list),settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_dict["Snippet"] = div.find_all("p")[1].text.strip()
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list