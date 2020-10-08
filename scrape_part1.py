import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument('--headless')

driver = webdriver.Chrome("./chromedriver", options=options)


def get_link_of_product(product_id):
    url = f'https://www.gewiss.com/ww/en/search?q={product_id}'
    driver.get(url)
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#resultsbox > div > div.results > div.resultslist.entries > div > a')))
    except TimeoutException:
        return ""

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_obj = soup.select_one('#resultsbox > div > div.results > div.resultslist.entries > div > a')
    product_link = f"https://www.gewiss.com/{product_obj['href']}"
    return product_link


in_file = open('files/product_list.csv')
out_file = open('files/product_list_with_links.csv', 'w')
reader = csv.reader(in_file)
writer = csv.writer(out_file)
for row in reader:
    prod_id = row[0]
    row.append(get_link_of_product(prod_id))
    writer.writerow(row)

driver.close()
