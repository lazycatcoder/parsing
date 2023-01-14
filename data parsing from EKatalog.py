#this script allows you to download a given category of goods from the EKatalog website and save it to a csv file

import requests
from bs4 import BeautifulSoup
import urllib.request as r
import json
from time import sleep
import csv
import random
import datetime

headers={
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

start_time=datetime.datetime.now()

#product category page (example)
link="https://ek.ua/ua/list/160/"  #select your product category (link as in the example)

link_category=link.split("/")[-2]
with r.urlopen("https://ek.ua/ua/list/"+f"{link_category}") as file:
    src=file.read().decode('utf-8')
    
soup=BeautifulSoup(src, "lxml")

#get category name
get_name_categories=soup.find(class_="page-title").find("h1").text.strip()
print(f"category: {get_name_categories}")

#extract all links from pagination
paginator_link=soup.find("div", class_="ib page-num").find_all("a")
last_page=(int(paginator_link[-1].text.strip()))
print(f"total pages: {last_page}")

all_links=[]
#for links in paginator_link[0:3]:
for links in paginator_link:
    all_links.append(links.get("href"))

first_link="https://ek.ua"+all_links[0]
#print(first_link)

all_pages_link=[]
for page in range(0, last_page+1):
    all_pages_link.append(first_link+f"{page}")
print(all_pages_link)

iteration_count = int(len(all_pages_link))
count = 0
print("-------------start---------------")

def write_csv():
    with open(f"{get_name_categories}.csv", "a", encoding="cp1251", newline="") as file:    #encoding="utf-8"
        writer=csv.writer(file, delimiter=",")
        writer.writerow(
            (
            title,
            price,
            link
            )
        ) 

for li in all_pages_link:
    print(f"total iterations: {iteration_count}")

    req = requests.get(url=li, headers=headers)
    sr = req.text
    prod = BeautifulSoup(sr, "lxml")
    print(f"received link: {li}")

    if count == 0:
        list=["TITLE", "PRICE", "LINK"]

        with open(f"{get_name_categories}.csv", "w", encoding="cp1251", newline="") as file:    #encoding="utf-8"
            writer=csv.writer(file, delimiter=",")
            writer.writerow(list)
            print("csv file is ready")
    else:
        print("csv file already created...")

    try:
        m_block=prod.find_all("table", class_="model-short-block")

        for b in m_block:
            price_flex=b.find("div", class_="d-flex align-items-start")
            price_range=b.find("div", class_="model-price-range")
            if price_flex:
                price=b.find("div", class_="pr31").text.strip()
                li=b.find("td", class_="model-short-info").find("a").get("onmouseover").split(";")[0].replace("this.href=", "")
                link="https://ek.ua" + li
                title=b.find("td", class_="model-short-info").find("a").text.strip()

                write_csv()

            elif price_range:
                pr=b.find("div", class_="model-price-range").find("a").text.strip()
                price="від "+pr
                title=b.find("span", class_="u").text.strip()
                li=b.find("td", class_="model-short-info").find("a").get("href")
                link="https://ek.ua" + li

                write_csv()

            else:
                price="not available"
                title=b.find("span", class_="u").text.strip()
                li=b.find("td", class_="model-short-info").find("a").get("href")
                link="https://ek.ua" + li

                write_csv()

    except Exception as ex:
        print(ex)

    count += 1
    iteration_count = iteration_count - 1

    if iteration_count == 0:
        print("script completed")
        end_time=datetime.datetime.now()
        total_time=end_time-start_time
        print(total_time)
        break