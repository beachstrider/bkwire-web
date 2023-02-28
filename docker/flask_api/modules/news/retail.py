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
                "https://retailbum.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            news_div_tag = soup.find("div", attrs={"role":"main"})
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
                "https://www.retaildive.com/search/?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li_tag in soup.find_all("li", limit=2, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("h3").text.strip()
                news_dict["Link"] = "https://www.retaildive.com" + li_tag.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = li_tag.find("h3").text.strip()
                news_dict["date"] = dateparser.parse(li_tag.find_all("span",class_="secondary-label")[1].text.split(":")[1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        try:
            response = requests.get(
                "https://www.businessinsider.in/searchresult.cms?query=retail+bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for section_tag in soup.find_all("section",class_="list-bottom-story",limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = section_tag.find("a", class_="list-title-link").text.strip()
                news_dict["Link"] = section_tag.find("a", class_="list-title-link",href=True)["href"]
                news_dict["Snippet"] = section_tag.find("div", class_="list-bottom-text").text.strip()
                news_dict["date"] = dateparser.parse(section_tag.find("div", class_="list-timestamp")["data-dateformat"],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fourth Website
        try:
            response = requests.get(
                "https://www.forbes.com/search/?q=retail%20bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a", class_="stream-item__title").text.strip()
                news_dict["Link"] = div.find("a", class_="stream-item__title", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="stream-item__description").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="stream-item__date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.modernretail.co/search/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            section_tag = soup.find("ul", class_="results")
            for li_tag in section_tag.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("h4").text.strip()
                news_dict["Link"] = li_tag.find("h4").find("a", href=True)["href"]
                news_dict["Snippet"] = li_tag.find("p").text.strip()
                news_dict["date"] = dateparser.parse(li_tag.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://omnitalk.blog/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2",class_="entry-title").text.strip()
                news_dict["Link"] = article.find("h2",class_="entry-title").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("div",class_="entry-content").find("p").text.strip()
                news_dict["date"] = dateparser.parse(article.find("time", class_="entry-time").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.businessoffashion.com/search/?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li_tag in soup.find_all("li", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li_tag.find("a").text.strip()
                news_dict["Link"] = "https://www.businessoffashion.com" + li_tag.find_parent("a", href=True)["href"]
                news_dict["Snippet"] = li_tag.find("a").text.strip()
                news_dict["date"] = dateparser.parse(li_tag.find("div",class_="searchpage-article-date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eighth Website
        try:
            response = requests.get(
                "https://nrf.com/search/bankruptcy?sort=field_date&order=desc",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="result-row"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = "https://nrf.com" + div.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="snippet").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Nineth Website
        try:
            response = requests.get(
                "https://sourcingjournal.com/results/#?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div_tag in soup.find_all("div", limit=2, class_="result-content"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div_tag.find("div",class_="result-title").text.strip()
                news_dict["Link"] = div_tag.find("div",class_="result-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div_tag.find("div",class_="text-block").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Tenth Website
        try:
            response = requests.get(
                "https://retailwire.com/search_gcse/?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="gsc-webResult gsc-result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div",class_="gs-title").text.strip()
                news_dict["Link"] = div.find("div",class_="gs-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div",class_="gs-bidi-start-align gs-snippet").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span", class_="full-date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 11th Website
        try:
            response = requests.get(
                "https://www.retailtouchpoints.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article_tag in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article_tag.find("h3").text.strip()
                news_dict["Link"] = article_tag.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = article_tag.find("div",attrs={"data-widget_type":"text-editor.default"}).text.strip()
                news_dict["date"] = dateparser.parse(article_tag.find("span", class_="elementor-icon-list-text").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list