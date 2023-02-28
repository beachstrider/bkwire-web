import datetime
import requests
import logging
from bs4 import BeautifulSoup
import dateparser
from .base import NewsScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FoodNewsScraper(NewsScraper):
    def get_news(self):
        news_list = super().get_news()

        # First Website
        try:
            response = requests.get(
                "https://www.fooddive.com/search/?q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for li in soup.find_all("li", limit=2, class_="row feed__item"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("h3", class_="feed__title").text.strip()
                news_dict["Link"] = ("https://www.fooddive.com"+ li.find("h3").find("a", href=True)["href"])
                news_dict["Snippet"] = li.find("h3", class_="feed__title").text.strip()
                news_dict["date"] = dateparser.parse(li.find_all("span")[-1].text.split(":")[-1],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Second Website 
        try:
            response = requests.get(
                "https://www.undercurrentnews.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="ucn-search-articles"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("a", attrs={"rel":"bookmark"}).text.strip()
                news_dict["Link"] = div.find("a", href=True, attrs={"rel":"bookmark"})["href"]
                news_dict["Snippet"] = div.find("p", class_="ucn-search-excerpt").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span",class_="ucn-search-date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

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
                "https://www.meatpoultry.com/search?page=1&q=bankruptcy&sort=date",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="records search-results")
            for div in soup.find_all("div", limit=3, class_="record"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="headline").text.strip()
                news_dict["Link"] = "https://www.meatpoultry.com" + div.find("h2", class_="headline").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="abstract").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Fifth Website
        try:
            url = "https://www.foodnavigator.com/search?q=bankruptcy&t=all&p=1&ob=date&range_date=date"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "Teaser-intro")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
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
                "https://www.provisioneronline.com/search?exclude_datatypes%5B%5D=video&exclude_datatypes%5B%5D=file&page=1&q=bankruptcy&sort=date",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="record"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="headline").text.strip()
                news_dict["Link"] = div.find("h2", class_="headline").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="abstract").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Seventh Website
        try:
            response = requests.get(
                "https://www.supermarketnews.com/search/node/bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("article", limit=2, class_="article-teaser__search article-teaser article-teaser__icon__article"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div", class_="title").text.strip()
                news_dict["Link"] = (
                    "https://www.supermarketnews.com" + div.find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("div", class_="summary").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("span", class_="date-display-single").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # eighth Website
        try:
            url = "https://progressivegrocer.com/search?q=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "teaser-card__content")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all("div", limit=2, class_="teaser-card__content"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="teaser-card__heading teaser-card__heading--").text.strip()
                news_dict["Link"] = (
                    "https://progressivegrocer.com"
                    + div.find("h2", class_="teaser-card__heading teaser-card__heading--").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("div", class_="teaser-card__body").text.strip()
                news_dict["date"] = dateparser.parse(div.find("span", class_="eyebrow").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # Nineth Website
        try:
            response = requests.get(
                "https://www.winsightgrocerybusiness.com/search/content?searchterm=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=1, class_="item item-list item-article item-article-list"
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

        # tenth Website
        try:
            response = requests.get(
                "https://www.foodtradenews.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="item-details"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3", class_="entry-title td-module-title").text.strip()
                news_dict["Link"] = div.find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="td-excerpt").text.strip()
                news_dict["date"] = dateparser.parse(div.find("time")["datetime"],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 11th Website
        try:
            response = requests.get(
                "https://theproducenews.com/search?search_api_fulltext=bankruptcy&field_primary_category=All&created=All&sort_by=search_api_relevance&sort_order=ASC",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all(
                "div", limit=2, class_="views-row"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("span", class_="field-content").text.strip()
                news_dict["Link"] = (
                    "https://theproducenews.com"
                    + div.find("span", class_="field-content").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("div", class_="views-field views-field-body").text.strip()
                news_dict["date"] = dateparser.parse(
                    div.find("div", class_="views-field views-field-created").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 12th Website
        try:
            url = "https://www.thepacker.com/search?fulltext=bankruptcy&sort_by=created"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
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
                news_dict["date"] = dateparser.parse(div.find("time")["datetime"],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error("SITE HAVE CAPTCHA")

        # 13th Website
        try:
            response = requests.get(
                "https://www.foodsafetynews.com/?s=bankruptcy",
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

        # 14th Website
        try:
            url = "https://www.seafoodsource.com/search?term=bankruptcy&searchCats=&sortOrder=pubDate"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "read-more-link")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all(
                "div", limit=1, class_="container--results-list ng-scope"
            ):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                news_dict["Link"] = (
                    "https://www.seafoodsource.com"
                    + div.find("h2").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = div.find("p", class_="ng-binding").text.strip()
                news_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")
                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 15th Website
        try:
            response = requests.get(
                "https://www.foodengineeringmag.com/search?exclude_datatypes%5B%5D=video&exclude_datatypes%5B%5D=file&page=1&q=bankruptcy&sort=date",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            div_tag = soup.find("div", class_="records search-results")
            for div in soup.find_all("div", limit=2, class_="record"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2", class_="headline").text.strip()
                news_dict["Link"] = div.find("h2", class_="headline").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="abstract").text.strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="date").text,settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 16th Website
        try:
            response = requests.get(
                "https://foodindustryexecutive.com/?s=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=1, class_="item-details"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h3", class_="entry-title td-module-title").text.strip()
                news_dict["Link"] = div.find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="td-excerpt").text.strip()
                news_dict["date"] = dateparser.parse(div.find("time")["datetime"],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 17th Website
        try:
            url = "https://www.beveragedaily.com/search?q=bankruptcy&t=all&p=1&ob=date&range_date=date"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "Teaser-intro")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for article in soup.find_all("article", limit=2, class_="Teaser"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = article.find("h3", class_="Teaser-title").text.strip()
                news_dict["Link"] = (
                    "https://www.beveragedaily.com"
                    + article.find("h3", class_="Teaser-title").find("a", href=True)["href"]
                )
                news_dict["Snippet"] = article.find("p", class_="Teaser-intro").text.strip()
                news_dict["date"] = dateparser.parse(
                    article.find("time", class_="Teaser-date").text,settings={'TIMEZONE': 'UTC'}
                ).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 18th Website
        try:
            response = requests.get(
                "https://www.bevnet.com/search?SearchFilter.SearchOnBevnet=true&SearchFilter.OrderBy=Date&q=bankruptcy",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.find_all("div", limit=2, class_="search-newsroll no-thumbnail"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("h2").text.strip()
                news_dict["Link"] = div.find("h2").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="content").text.split("...")[1].strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="content").text.split("...")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        # 19th Website
        try:
            url = "https://www.foodmanufacturing.com/search?q=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "gs-title")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for div in soup.find_all("div", limit=2, class_="gsc-webResult gsc-result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = div.find("div",class_="gs-title").text.strip()
                news_dict["Link"] = div.find("div",class_="gs-title").find("a", href=True)["href"]
                news_dict["Snippet"] = div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[1].strip()
                news_dict["date"] = dateparser.parse(div.find("div", class_="gs-bidi-start-align gs-snippet").text.split("...")[0],settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(f"Site Have Dynamic Content {exception_msg}")

        # 20th Website
        # Selenium Driver Headless Chrome
        try:
            url = "https://www.foodprocessing.com/search?q=bankruptcy"
            options = Options()
            options.headless = True
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            div_result = soup.find("div", attrs={"id":"search_results"})
            for li in div_result.find_all("div", limit=2, class_="result"):
                news_dict = {"Title": None, "Link": None, "Snippet": None, "date": None}
                news_dict["Title"] = li.find("a").text
                news_dict["Link"] = li.find("a", href=True)["href"]
                news_dict["Snippet"] = li.find("p").text.strip()
                news_dict["date"] = dateparser.parse(li.find("span", class_="date-proper").text.strip(),settings={'TIMEZONE': 'UTC'}).strftime("%Y-%m-%d")

                news_list.append(news_dict)
        except Exception as exception_msg:
            logging.error(exception_msg)

        return news_list