import datetime
import requests
import logging
import dateparser
from bs4 import BeautifulSoup
from .base import NewsScraper


class RetailNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://retailbum.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            news_div_tag = soup.find("div", class_="wpb_wrapper")
            for (div_tag, li_tag) in zip(
                news_div_tag.find_all("div", limit=2, class_="post-title"),
                news_div_tag.find_all("li", limit=2, class_="post-date"),
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div_tag.text.strip()
                news_dict["Link"] = div_tag.find("a", href=True)["href"]
                news_dict["Snippet"] = div_tag.text.strip()
                news_dict["date"] = dateparser.parse(li_tag.text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.retaildive.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li_tag in soup.find_all("li", limit=2, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.retaildive.com"
                    + li_tag.find("h3").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li_tag.find(
                    "p", class_="feed__description"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.businessinsider.com/retail",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for (anchor_tag, div_tag, date_div_tag) in zip(
                soup.find_all("a", limit=2, class_="list-title-link"),
                soup.find_all("div", limit=2, class_="list-top-text"),
                soup.find_all("div", limit=2, class_="list-timestamp"),
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

        # Fourth Website
        try:
            response = requests.get(
                "https://www.forbes.com/retail/?sh=511944b44a82",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="latest-picks")
            for div in div_tag.find_all("div", limit=2, class_="section-pick"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find(
                    "a", class_="section-pick__title"
                ).text.strip()
                news_dict["Link"] = div.find("a", class_="section-pick__title", href=True)[
                    "href"
                ]
                news_dict["Snippet"] = div.find(
                    "a", class_="section-pick__title"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.modernretail.co/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            section_tag = soup.find("section", attrs={"id": "latest_stories"})
            for div in section_tag.find_all("div", limit=2, class_="block-text"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h4").text.strip()
                news_dict["Link"] = div.find("h4").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://omnitalk.blog/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="nextfeatured-single", attrs={"style": ""}
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h4").text.strip()
                news_dict["Link"] = div.find("h4").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("h4").text.strip()
                try:
                    news_dict["date"] = dateparser.parse(
                        div.find("div", class_="maindate").text,settings={'TIMEZONE': 'UTC'}
                    ).strftime("%Y-%m-%d")
                except:
                    news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.businessoffashion.com/news/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="list-item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                news_dict["Link"] = (
                    "https://www.businessoffashion.com"
                    + div.find("h2").find_parent("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eighth Website
        try:
            response = requests.get(
                "https://nrf.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="card-33 image tall"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find(
                    "div", class_="card-title card-33-title"
                ).text.strip()
                news_dict["Link"] = (
                    "https://nrf.com"
                    + div.find("div", class_="card-url card-33-url").find("a", href=True)[
                        "href"
                    ]
                )
                news_dict["Snippet"] = div.find(
                    "div", class_="card-description card-33-description"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Nineth Website
        try:
            response = requests.get(
                "https://sourcingjournal.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for h3_tag in soup.find_all("h3", limit=2, attrs={"id": "title-of-a-story"}):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = h3_tag.text.strip()
                news_dict["Link"] = h3_tag.find("a", href=True)["href"]
                news_dict["Snippet"] = h3_tag.text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Tenth Website
        try:
            response = requests.get(
                "https://retailwire.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="sub-list-post not-thumbnail"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = div.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("h3").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="full-date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 11th Website
        try:
            response = requests.get(
                "https://www.retailtouchpoints.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            article_tag = soup.find("article")
            news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
            news_dict["Title"] = article_tag.find("h2").text.strip()
            news_dict["Link"] = article_tag.find("h2").find("a", href=True)["href"]
            news_dict["Snippet"] = article_tag.find("h2").text.strip()
            news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
            news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list
