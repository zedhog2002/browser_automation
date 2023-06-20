from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
from fake_useragent import UserAgent
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
import requests
from selenium.webdriver.common.by import By

useragent = UserAgent()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={useragent}")
driver = webdriver.Chrome(executable_path=r"C:\Users\kings\Downloads\chromedriver_win32", options=options)


def open_url(place, thing):
    global driver
    driver.get(f"https://www.justdial.com/{place}/{thing}/")
    close = driver.find_element(By.CLASS_NAME, 'white_close_icon')
    close.click()
    time.sleep(1)
    list = driver.find_element(By.CLASS_NAME, 'filter_drop_icon')
    list.click()
    time.sleep(1)
    sort = driver.find_element(By.XPATH, "//span[@class='jsx-6ab5af3a8693e5db animtext'][text()='Rating']")
    sort.click()
    time.sleep(1)

    scroll_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # load whole page
        try:
            close_popup = driver.find_element(By.ID, 'onCloseMobile')
            close_popup.click()
        except:
            pass
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight - 4000);")
        time.sleep(2)
        new_scroll_height = driver.execute_script("return document.body.scrollHeight")
        if new_scroll_height == scroll_height:
            break
        scroll_height = new_scroll_height
    # extract page's html
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # extract title of shop
    results_title = soup.find_all('h2', class_='resultbox_title')
    titles = [result.get_text(strip=True) for result in results_title]

    # extract the address of shop
    results_address = soup.find_all('div', class_='resultbox_address')
    addresses = [result.get_text(strip=True) for result in results_address]

    # Save data into CSV
    filename = f"{place}_{thing}_data.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(['Title', 'Address'])
        writer.writerows(zip(titles, addresses))

    print(f"Data saved to '{filename}'")


open_url('mumbai', 'chemist')
