#this script saves information about all the restaurants in the selected city

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import sqlite3 as sq
import pandas as pd
import csv
import os
import random


user_agents=["Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0", 
"Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
"Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
"Mozilla/5.0 (X11; CrOS x86_64 14816.99.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
"Mozilla/5.0 (X11; CrOS x86_64 13982.88.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.162 Safari/537.36"]

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }

options=webdriver.ChromeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")
# options.headless=True
driver=webdriver.Chrome(executable_path=r"D:\chromedriver.exe", options=options) #link to web driver

url="https://www.tripadvisor.com/RestaurantSearch-g295377-Lviv_Lviv_Oblast.html"  #link of the required city with restaurants (link as in the example)


with sq.connect(r'D:\tripadvisor.db') as con: #select your directory
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS restaurants
        (
            Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            Price TEXT,
            Cuisine TEXT,
            Rating INTEGER,
            Address TEXT,
            Tel TEXT,
            Email TEXT,
            Site TEXT,
            Menu TEXT,
            Hours TEXT,
            Url_res TEXT,
            Date TEXT
        )'''
    )
    cur.execute('''CREATE TABLE IF NOT EXISTS page_links
        (
            Num_trip INTEGER NOT NULL,
            Title TEXT,
            Link TEXT
        )'''
    )
    

    def change_url(link_index):
        split_link=url.split("-")
        split_link.insert(2, f"oa{link_index}")
        url_upd="-".join(split_link)
        return url_upd


    def search_elem_pags():
        try:
            amount_restaurants=driver.find_element(By.XPATH, "//span[@class='SgeRJ']").find_element(By.XPATH, "//span[@class='b']").text
            amount_restaurants=int(amount_restaurants)
            print(f"Number of restaurants: {amount_restaurants}")
            pages=int((amount_restaurants/30)+1)
            print(f"Number of pages to search: {pages}")      
        except:
            amount_restaurants=driver.find_elements(By.XPATH, "//a[@class='Lwqic Cj b']")
            amount_restaurants=int(len(amount_restaurants))
            print(f"Number of restaurants: {amount_restaurants}")
            pages=int((amount_restaurants/30)+1)
            print(f"Number of pages to search: {pages}") 
        return amount_restaurants, pages
    

    def database_get_pages_info(title_r, num_trip, get_lin):
        print("launch -database_get_pages_info-")
        title_r, num_trip, get_lin
        while True:
            try:
                print("link check...")
                find_lin=cur.execute(f"SELECT Title FROM page_links WHERE Title = \'{title_r}\' AND Link = \'{get_lin}\'")
                if len(list(find_lin)) == 0:
                    print("------------writing--------------\n")
                    ins=cur.execute("INSERT INTO page_links (Num_trip, Title, Link) VALUES (?,?,?)", (num_trip, title_r, get_lin))
                    con.commit()
                else:
                    print("-------------skip--------------\n")
                    pass
            except:
                print("Error writing")
                time.sleep(2)
                continue
            break
    

    def get_pages_info(get_pages_restaurants):
        print("launch -get_pages_info-")
        for page in get_pages_restaurants:
            while True:
                try:
                    title=page.text.replace("'", "").strip().split(" ")[1:]
                    title_r="".join(title)
                    print(title_r)

                    num_trip=page.text.strip().split(" ")[0].replace(".", "")

                    get_lin=page.get_attribute('href')
                    print(get_lin)
                except:
                    continue
                break
            database_get_pages_info(title_r, num_trip, get_lin)


    def database_rest_info(title, price, cuisine, rating, address, tel, email, site, menu, hours, url_res, date):
        print("launch -database_rest_info-")
       
        title, price, cuisine, rating, address, tel, email, site, menu, hours, url_res, date
        print("get funk -get_rest_info-")
        try:
            print("restaurant check...")
            find_res=cur.execute(f"SELECT Title FROM restaurants WHERE Url_res = \'{url_res}\'")
            if len(list(find_res)) == 0:
                print("restaurant not found. writing...\n")
                ins=cur.execute("INSERT INTO restaurants (Title, Price, Cuisine, Rating, Address, Tel, Email, Site, Menu, Hours, Url_res, Date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (title, price, cuisine, rating, address, tel, email, site, menu, hours, url_res, date))
                con.commit()
                print("databases-ok\n")
            else:
                pass
        except:
            print("update error\n")
        

    def get_rest_info(get_link):
        driver.get(url=get_link)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("--------------------------------------------------------------------------")
        try: 
            price=driver.find_element(By.XPATH, "//div[text()='PRICE RANGE']/following::div[1]").text
            print(price)
        except:
            price=""

        try:
            site=driver.find_element(By.XPATH, "//span[@class='DsyBj cNFrA'][3]//a").get_attribute('href')
            print(site)
        except:
            site="" 
              
        try:
            menu=driver.find_element(By.XPATH, "//span[@class='DsyBj cNFrA AsyOO']//a").get_attribute('href')
            print(menu)
        except:
            menu=""

        url_res=driver.current_url
        req_res=requests.get(url=url_res, headers=headers)
        src_res=req_res.text
        soup_res=BeautifulSoup(src_res, "lxml")
        
        title=soup_res.find("h1", class_="HjBfq").text.replace("'", "")
        print(title)
    
        try: 
            cuisine_list=[]
            cuisine_inf=soup_res.find(class_="DsyBj DxyfE")
            for i in cuisine_inf: 
                cuisine_list.append(i.text)
            cuisine=" ".join(cuisine_list)
            print(cuisine)
        except:
            cuisine=""

        try:
            rating=soup_res.find(class_="ZDEqb").text
            print(rating)
        except:
            rating="" 

        try:
            email=soup_res.find_all("div", class_="IdiaP Me sNsFa")[1].find("a").get("href").replace(":", "?").split("?")[1]
            print(email)
        except:
            email=""

        try:
            res_inf=soup_res.find_all("div", class_="vQlTa H3")[1]
            address=res_inf.find("span", class_="DsyBj cNFrA").text
            print(address)
        except:
            address="" 

        try:
            tel=res_inf.find("span", class_="AYHFM").text.replace(" ", "").replace("-", "")
            print(tel)
        except:
            tel=""

        try:
            hours=res_inf.find("div", class_="NehmB").text.strip()
            print(hours)
        except:
            hours=""

        url_res=get_link
        get_date=datetime.now()
        date=get_date.strftime("%d.%m.%Y; %H:%M:%S")
        print(date)
        print("--------------------------------------------------------------------------")
        database_rest_info(title, price, cuisine, rating, address, tel, email, site, menu, hours, url_res, date)


    def get_info():
        db_links=cur.execute("SELECT Link FROM page_links").fetchall()
        get_links=list(map(lambda x: str(x[0]), db_links))
        for get_link in get_links:
            print(get_link)
            find_res_1=cur.execute(f"SELECT * FROM restaurants WHERE Url_res = \'{get_link}\'")
            if len(list(find_res_1)) > 0:
                print("--------------found. skipping...----------------")
                pass
            else:
                print("launch -get_rest_info-")
                get_rest_info(get_link)
                

    def main():
        link_index=0
        score=1
        try:
            driver.get(url=url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            amount_restaurants, pages = search_elem_pags()
            print("search_elem_pags")

            top_res=driver.find_element(By.XPATH, "//div[@class='pFMac b Cj']").text

            tab_links=cur.execute("SELECT COUNT (Title) FROM page_links").fetchone()[0]
            print(f"number of wrote restaurants in the DB: {tab_links}")
            print("-----------------------------------------------------------------")

            if tab_links != amount_restaurants:                     
                print(f"DB {top_res} is incomplete. Wait\n")
                while score<=pages:
                    print("*******************************************************************")
                    print(f"page: {score} / {pages}\n")
                    print(f"link index: {link_index} / {amount_restaurants}")
                    
                    url_restaurants=change_url(link_index)
                    print(url_restaurants)
                    print("*******************************************************************\n")

                    driver.get(url=url_restaurants)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    get_pages_restaurants=driver.find_elements(By.XPATH, "//a[@class='Lwqic Cj b']")
                    print("number of restaurant links per page")
                    print(int(len(get_pages_restaurants)))
                    print("\n")
                    # time.sleep(2)
                    print(get_pages_restaurants)

                    print("launch -get_pages_info-")
                    get_pages_info(get_pages_restaurants)

                    print("links added - ok")
                    
                    score+=1
                    link_index+=30

                    if score>pages:
                        print("stop")
                        break

                print(f"the database of restaurants in {top_res} is ready. launch -get_info-\n")
                get_info()
            else:
                print(f"the database of restaurants in {top_res} is ready. launch -get_info\n")
                get_info()

        except:
            print("something wrong")
        finally:
            driver.close()
            driver.quit()
            print("close - ok")

    if __name__ == "__main__":
        main()

    query="SELECT * FROM restaurants"
    data=pd.read_sql(query, con)
    data.to_csv(r'D:\export_tripadvisor.csv', encoding='utf-8', index=False)
    print("csv - ok")