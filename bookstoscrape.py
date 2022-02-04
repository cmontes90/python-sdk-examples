import requests
from bs4 import BeautifulSoup
import pandas as pd

pages = []
titles = []
prices = []
ratings = []
urls = []

pages_to_scrape = 1

for i in range(1, pages_to_scrape + 1):
    url = f"https://books.toscrape.com/catalogue/page-{i}.html"
    pages.append(url)

for item in pages:
    page = requests.get(item)
    soup = BeautifulSoup(page.text, "html.parser")
    # print(soup.prettify())
    for i in soup.select("a[title]"):
        title = i.attrs["title"]
        titles.append(title)
    for j in soup.find_all("p", class_="price_color"):
        price = j.get_text()
        price_new = price.replace("Â", "")
        prices.append(price_new)
    for s in soup.find_all("p", class_="star-rating"):
        for k, v in s.attrs.items():
            rating = v[1]
            ratings.append(rating)
    for x in soup.find_all("img", class_="thumbnail"):
        thumb = x["src"]
        url = f"https://books.toscrape.com/{thumb}"
        new_url = url.replace("..", "")
        urls.append(new_url)

data_dict = {"Title": titles, "Price": prices, "Rating": ratings, "Img_url": urls}
df = pd.DataFrame(data=data_dict)
df.index += 1
df.to_excel("/home/cmontes/bookstoscrape/output.xlsx")4