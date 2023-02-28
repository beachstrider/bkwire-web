import datetime
import requests
import logging
from bs4 import BeautifulSoup
import dateparser
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class FoodNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.fooddive.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find(
                    "h3", class_="feed__title feed__title--display"
                ).text.strip()
                news_dict["Link"] = (
                    "https://www.fooddive.com"
                    + li.find("h3", class_="feed__title feed__title--display").find(
                        "a", href=True
                    )["href"]
                )
                news_dict["Snippet"] = li.find("p", class_="feed__description").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website
        try:
            response = requests.get(
                "https://www.undercurrentnews.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for h3 in soup.find_all("h3", limit=2, class_="latest-news-heading"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = h3.find("a").text.strip()
                news_dict["Link"] = h3.find("a", href=True)["href"]
                news_dict["Snippet"] = h3.find("a").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Third Website
        response = requests.get(
            "https://www.producemarketguide.com/",
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
            },
        )
        soup = BeautifulSoup(response.content, "html.parser")
        try:
            for div in soup.find_all("div", limit=2, class_="teaser"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a", class_="field--name-title").text.strip()
                news_dict["Link"] = (
                    "https://www.producemarketguide.com" + div.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find(
                    "div", class_="field--name-body"
                ).text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="field--name-changed").text.split("by")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"SITE HAVE GOOGLE CAPTCHA {exception_msg}")

        # Fourth Website
        try:
            response = requests.get(
                "https://www.meatpoultry.com/articles/topic/260-news",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="records")
            for article in div_tag.find_all(
                "article", limit=2, class_="record article-summary"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find(
                    "h2", class_="headline article-summary__headline"
                ).text.strip()
                news_dict["Link"] = article.find(
                    "h2", class_="headline article-summary__headline"
                ).find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("div", class_="date article-summary__post-date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            response = requests.get(
                "https://www.foodnavigator.com/Sectors/Meat#",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2, class_="Teaser"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3", class_="Teaser-title").text.strip()
                news_dict["Link"] = (
                    "https://www.foodnavigator.com"
                    + article.find("h3", class_="Teaser-title").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find("p", class_="Teaser-intro").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("time", class_="Teaser-date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Sixth Website
        try:
            response = requests.get(
                "https://www.meatingplace.com/Industry/News",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for h1 in soup.find_all("h1", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = h1.find("a", class_="link").text.strip()
                news_dict["Link"] = (
                    "https://www.meatingplace.com"
                    + h1.find("a", class_="link", href=True)["href"]
                )
                news_dict["Snippet"] = h1.find("a", class_="link").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.provisioneronline.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="featured-news__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find(
                    "h1", class_="featured-news__headline"
                ).text.strip()
                news_dict["Link"] = li.find(
                    "a", class_="featured-news__article-title-link", href=True
                )["href"]
                news_dict["Snippet"] = li.find(
                    "div", class_="featured-news__teaser"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eigth Website
        try:
            response = requests.get(
                "https://www.thebeefsite.com/news/vars/country/us/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="newsIndexItem"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.a.find_next_sibling("a").text.strip()
                news_dict["Link"] = (
                    "https://www.thebeefsite.com" + div.a.find_next_sibling("a")["href"]
                )
                news_dict["Snippet"] = div.text.split('"')[-1].strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Ninth Website
        try:
            response = requests.get(
                "https://www.supermarketnews.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="article-teaser__header"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="title").text.strip()
                news_dict["Link"] = (
                    "https://www.supermarketnews.com" + div.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("div", class_="title").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="date-display-single").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Tenth Website
        try:
            response = requests.get(
                "https://progressivegrocer.com/supermarket-grocery-industry-news",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="card card--"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h2", class_="card__heading").text.strip()
                news_dict["Link"] = (
                    "https://progressivegrocer.com"
                    + li.find("h2", class_="card__heading").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = li.find("div", class_="card__body").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Eleventh Website
        try:
            response = requests.get(
                "https://www.winsightgrocerybusiness.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="item item-list item-article item-article-list"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3", class_="title").text.strip()
                news_dict["Link"] = (
                    "https://www.winsightgrocerybusiness.com"
                    + div.find_all("a", href=True)[1]["href"]
                )
                news_dict["Snippet"] = div.find("p", class_="dek").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 12th Website
        try:
            response = requests.get(
                "https://www.foodtradenews.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find_all("div", class_="td_block_inner td-mc1-wrap")[2]
            for div in div_tag.find_all("div", limit=2, class_="td-module-meta-info"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find(
                    "h3", class_="entry-title td-module-title"
                ).text.strip()
                news_dict["Link"] = div.find("a", href=True)["href"]
                news_dict["Snippet"] = div.find(
                    "h3", class_="entry-title td-module-title"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 13th Website
        try:
            response = requests.get(
                "https://theproducenews.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="card-item extra-tile views-row"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("span", class_="field-content").text.strip()
                news_dict["Link"] = (
                    "https://theproducenews.com"
                    + div.find("span", class_="field-content").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("span", class_="field-content").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="views-field views-field-created").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 14th Website
        try:
            response = requests.get(
                "https://www.thepacker.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="region region-content")
            for div in div_tag.find_all("div", limit=2, class_="teaser"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = (
                    div.find("div", class_="col").find("a").text.strip()
                )
                news_dict["Link"] = (
                    "https://www.thepacker.com"
                    + div.find("div", class_="col").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("p").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error("SITE HAVE CAPTCHA")

        # 15th Website
        try:
            response = requests.get(
                "https://www.foodsafetynews.com",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h1").text.strip()
                news_dict["Link"] = article.find("h1").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("p").text.strip()
                news_dict["date"] = dateparser.parse(article.find("time")["datetime"],settings={'TIMEZONE': 'UTC'}).strftime(
                    "%Y-%m-%d"
                )
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 16th Website
        try:
            response = requests.get(
                "https://www.seafoodnews.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="mason hover-change"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("span", class_="StoryTitle").text.strip()
                news_dict["Link"] = (
                    "https://www.seafoodnews.com"
                    + div.find("a", href=True, class_="blklnks")["href"]
                )
                if div.find_all("p")[1].text.strip() == "":
                    news_dict["Snippet"] = div.find_all("p")[2].text.strip()
                else:
                    news_dict["Snippet"] = div.find_all("p")[1].text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 17th Website
        try:
            response = requests.get(
                "https://www.seafoodsource.com/news",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="t3p0-row row collection--field-mapping"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                news_dict["Link"] = (
                    "https://www.seafoodsource.com"
                    + div.find("h2").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("h2").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 18th Website
        try:
            response = requests.get(
                "https://www.foodengineeringmag.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="featured-news__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h1").text.strip()
                news_dict["Link"] = li.find("h1").find("a", href=True)["href"]
                news_dict["Snippet"] = li.find(
                    "div", class_="featured-news__teaser"
                ).text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 19th Website
        try:
            response = requests.get(
                "https://foodindustryexecutive.com/category/industry-pr/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="td_module_1 td_module_wrap td-animation-stack"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3").text.strip()
                news_dict["Link"] = div.find("h3").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("h3").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("time")["datetime"].split("T")[0],settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 20th Website
        try:
            response = requests.get(
                "https://www.beveragedaily.com",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2, class_="Teaser"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3").text.strip()
                news_dict["Link"] = (
                    "https://www.beveragedaily.com"
                    + article.find("h3").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find("h3").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 21th Website
        try:
            response = requests.get(
                "https://bevnet.com",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", limit=2, class_="featured-post hentry"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h2").text.strip()
                news_dict["Link"] = article.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = article.find("h2").text.strip()
                news_dict["date"] = dateparser.parse(article.find("time")["datetime"],settings={'TIMEZONE': 'UTC'}).strftime(
                    "%Y-%m-%d"
                )
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 22th Website
        response = requests.get(
            "https://www.foodmanufacturing.com/",
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
            },
        )
        soup = BeautifulSoup(response.content, "html.parser")
        try:
            for div in div_tag.find_all("div", limit=2, class_="node__contents"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h5").text.strip()
                news_dict["Link"] = (
                    "https://www.foodmanufacturing.com"
                    + div.find("h5").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("h5").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"Site Have Dynamic Content {exception_msg}")

        # 23th Website
        # Selenium Driver Headless Chrome
        try:
            url = "https://www.foodprocessing.com/industrynews/"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for li in soup.find_all("li", limit=3, class_="articles-index-list-item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("a").text
                news_link = li.find("a", href=True)
                news_dict["Link"] = "https://www.foodprocessing.com" + news_link["href"]
                news_dict["Snippet"] = li.find("h2", class_="deck").text.strip()
                news_dict["date"] = dateparser.parse(
                    li.find("div", class_="date").text.strip(),settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list
