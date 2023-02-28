import dateparser
import requests
from bs4 import BeautifulSoup
import logging
from .base import NewsScraper

class TransportationNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.freightwaves.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=5, class_="post-details"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = div.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("p", class_="post-excerpt").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span",class_="date meta-item tie-icon").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.ttnews.com/search/results/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div_tag in soup.find_all("div", limit=5, class_="clearfix non-sponsored"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div_tag.find("h4").text.strip()
                news_dict["Link"] = "https://www.ttnews.com" + div_tag.find("h4").find("a", href=True)["href"]
                news_dict["Snippet"] = div_tag.find("div",class_="text").find("p").text.strip()
                news_dict["date"] = dateparser.parse(div_tag.find("span",class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website inprogress
        try:
            response = requests.get(
                "https://www.scmr.com/search/resultsbydate/search&keywords=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="unprotectedstorybody")
            for (span_tag,br_tag) in zip(div_tag.find_all("span", class_="blogrolltitle",limit=4),
                                        div_tag.find_all('br',attrs={"clear":"left"},limit=4),
                                        ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = span_tag.find("a").text.strip()
                news_dict["Link"] = "https://www.scmr.com" + span_tag.find("a")["href"]
                news_dict["Snippet"] = br_tag.previous_sibling.strip()
                news_dict["date"] = dateparser.parse(" ".join(span_tag.next_sibling.next_sibling.next_sibling.strip().split("\n")[-1].strip().split(" ")[:3]),settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.logisticsbusiness.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2").text.strip()
                news_dict["Link"] = article.find("h2").find("a")["href"]
                news_dict["Snippet"] = article.find("section",class_="entry-content").find("p").text.strip()
                news_dict["date"] = dateparser.parse(article.find("p",class_="byline").text.split("-")[1].split(";")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website 
        try:
            response = requests.get(
                "https://www.supplychaindive.com/search/?q=bankruptcy&selected_facets=section_exact%3Anews&topics=&sortby=on",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li_tag in soup.find_all("li", limit=5, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("h3").text.strip()
                news_dict["Link"] = ("https://www.supplychaindive.com" + li_tag.find("h3").find("a", href=True)["href"])
                news_dict["Snippet"] = li_tag.find("h3").text.strip()
                news_dict["date"] = dateparser.parse(li_tag.find_all("span",class_="secondary-label")[1].text.split(":")[1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list