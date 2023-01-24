#this script saves the list of new movies from Hdrezka website to a csv file and DB

import requests
from bs4 import BeautifulSoup
import datetime
import re
import csv
import os
from time import sleep
import random
import sqlite3 as sq
import pandas as pd


with sq.connect(r'D:\movies.db') as con: #select your directory
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS mov
        (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            series TEXT,
            year TEXT,
            genre TEXT,
            country TEXT,
            duration TEXT,
            imdb REAL,
            img TEXT,
            link TEXT,
            date TEXT
        )'''
    )

    start_time=datetime.datetime.now()
    print(f"start time: {start_time}")

    url="https://rezka.ag/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }

    req=requests.get(url=url, headers=headers)
    src=req.text
    soup=BeautifulSoup(src, "lxml")

    def check_mov():
        print("checking movies...")
        find_title=cur.execute(f"SELECT * FROM mov WHERE title = \'{title_1}\'")

        if len(list(find_title)) == 0:
            print("movie not found. writing...\n")
            ins=cur.execute("INSERT INTO mov (title, series, year, genre, country, duration, imdb, img, link, date) VALUES (?,?,?,?,?,?,?,?,?,?)", (title_1, series_1, year_1, genre_1, country_1, duration_1, imdb_1, img_1, link_1, date_1))
            con.commit()
        else:
            print("movie was found. checking new episodes... \n")
            find_series=cur.execute(f"SELECT series FROM mov WHERE title = \'{title_1}\'")
            find_series=cur.fetchone()
            print(find_series[0])
            if f"{series_1}" == find_series[0]:
                print("new episodes not found. skip...")
                pass
            else:
                print("found new episodes. writing...")
                up=cur.execute(f"UPDATE mov SET series=\'{series_1}\', date=\'{date_1}\' WHERE title = \'{title_1}\'")
                con.commit()
                print("new series updated")

    newest_cont=soup.find(id="newest-slider-content").find_all("div", class_="b-content__inline_item")
    count=1

    for cont in newest_cont:
        print(f"---------------------{count}---------------------")
        title_1=cont.find("div", class_="b-content__inline_item-link").find("a").text.strip()
        print(title_1)
        gen=cont.find("div", class_="b-content__inline_item-link").find(class_="misc").text.split(",")
        year_1=gen[0].strip()
        print(year_1)
        country_1=gen[1].strip()
        print(country_1)
        genre_1=gen[2].strip()
        print(genre_1)
        link_1="https://rezka.ag"+cont.find("div", class_="b-content__inline_item-link").find("a").get("href").strip()
        print(link_1)
        
        try:
            se=cont.find_all("span", class_="info")
        except Exception:
            print("something wrong...")

        if se:    
            ser=cont.find("div", class_="b-content__inline_item-cover").find("a").find("span", class_="info").text.strip()
            series_1="сериал: "+re.sub(r'сезон', 'сезон ', ser)
            print(series_1)
        else:
            series_1="фильм"
            print(series_1)

        requ=requests.get(url=link_1, headers=headers)
        sr=requ.text
        data=BeautifulSoup(sr, "lxml")

        img_1=data.find("div", class_="b-sidecover").find("a").get("href")
        print(img_1)
        imdb_1=data.find("span", class_="b-post__info_rates imdb").find("span", class_="bold").text
        print(imdb_1)
        try:
            duration_1=data.find("div", class_="b-post__infotable_right_inner").find("td", itemprop="duration").text
            print(duration_1)
        except:
            duration_1=""

        date_1=datetime.date.today()
        print(date_1)
    
        print("......checking the movie in DB......")
        check_mov()

        #sleep(random.randrange(1, 3))
        count+=1

    query="SELECT * FROM mov"
    data=pd.read_sql(query, con)
    data.to_csv(r'D:\export_mov.csv', encoding='cp1251', index=False) #select your directory

    print("--------------------------")
    end_time=datetime.datetime.now() #"%d/%m/%y %H:%M"
    total_time=end_time-start_time
    print("script completed")
    print(total_time)