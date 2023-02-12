# This script collects photos from the selected account using another online application

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import os
import random
import datetime
 

user_agents=["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36", 
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"]

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }

options=webdriver.ChromeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")
# options.headless=True
driver=webdriver.Chrome(executable_path=r"D:\chromedriver.exe", options=options) #link to web driver

link="https://www.instagram.com/instagram"  #link to account (link as in the example)

user_name=""        #your login
user_pass=""        #your password


def login():
    driver.get(url="https://www.instagram.com/accounts/login")
    # time.sleep(3)
    driver.implicitly_wait(3)
    user_name_login=driver.find_element(By.NAME, 'username')
    user_name_login.clear()
    user_name_login.send_keys(f"{user_name}")
    print("login - ok")

    user_name_pass=driver.find_element(By.NAME, 'password')
    user_name_pass.clear()
    user_name_pass.send_keys(f"{user_pass}")
    print("password - ok\n")
    time.sleep(2)
    user_name_pass.send_keys(Keys.ENTER)
    #button_click-driver.find_element(By.CLASS_NAME, '').click()
    print("authorization was successful!\n")
    time.sleep(5)
    

def create_folder(workspace, folder):
    path = os.path.join(workspace, folder)
    if not os.path.exists(path):
        os.makedirs(path)
        print("create folder with path {0}".format(path))
    else:
        print("folder {0} exists ".format(path))


def main():
    try:
        login()
        driver.get(url=link)
        time.sleep(2)

        get_username=link.split("/")[-1]
        print(f"selected user: {get_username}")

        posts=driver.find_element(By.XPATH, "//ul[@class='_aa_7']//child::span").text
        posts=int(posts.replace(",", ""))
        print(f"total posts: {posts}")
        print("\n")

        if posts == 0:
            print(f"user {get_username} hasn't any posts")
        else:
            while True:
                try:
                    input_posts=int(input(f"enter the number of posts (from 1 to {posts}): "))
                    if 1 <= input_posts <= posts:
                        print(f"the first {input_posts} posts will be downloaded now") 
                        break  
                    else:
                        print(f"please enter the number of posts (from 1 to {posts}): ")
                except:
                    print("please enter number")

            
            print("checking the folder in current directory...\n")
            create_folder(".\instagram", f"{get_username}")

            print("downloading posts...\n")
            
            down_page_count=int((input_posts/12)+1)

            get_all_elems=[]   
            while down_page_count>0:
                print(f"-----------pages left: {down_page_count}-----------")
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # driver.implicitly_wait(2) 
                time.sleep(2)

                collect_links=driver.find_elements(By.XPATH, "//div[@class='_aabd _aa8k _aanf']//child::a")
                for collect_link in collect_links:
                    li=collect_link.get_attribute('href')
                    get_all_elems.append(li)

                down_page_count-=1
                if down_page_count==0:
                    break

            print(get_all_elems)

            links=[]
            len_link=1
           
            get_all_links = []
            for el in get_all_elems:
                if el not in get_all_links:
                    get_all_links.append(el)
            
            print(get_all_links)

            for get_one_link in get_all_links:
                if len_link <= input_posts:
                    links.append(get_one_link)
                    len_link+=1
                else:
                    print("all links have been collected\n")
                    break

            print(links)

            len_links=int(len(links))

            count_img=0

            for lin in links:
                print(f"-----------------{len_links} links left-----------------")
                driver.get(url="https://en.savefrom.net/163/download-from-instagram")
                driver.implicitly_wait(3)

                search_li=driver.find_element(By.NAME, 'sf_url')
                search_li.clear()
                search_li.send_keys(f"{lin}")
                print("link added\n")
                driver.implicitly_wait(3)
                search_li.send_keys(Keys.ENTER)
                driver.implicitly_wait(5)
                
                src_links=driver.find_elements(By.XPATH, "//div[@class='link-box single']//a")
                elem=int(len(src_links))
                print(elem)
                for src_link in src_links:
                    sr=src_link.get_attribute("href")
                    print(sr)
                    index = sr.find(".mp4")

                    if index>=0:
                        print("the post contains video. skip...")
                        pass
                    else:
                        name_link_img=sr.split("?")[0].split("/")[-1]
                        output_date = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                        p = requests.get(sr)
                        with open(f".\\instagram\\{get_username}\\{output_date}_{name_link_img}", "wb") as img:
                            img.write(p.content)
                        print("file saved")
                        count_img+=1
                
                len_links-=1

            print(f"from {posts} posts downloaded {count_img} photos")
    except:
        print("something wrong!")
    finally:
        print("task completed")
        driver.close()
        driver.quit()


if __name__ == "__main__":
    main()