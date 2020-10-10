import os
import csv
import json
import requests
import pathlib
import threading
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument('--headless')

DRIVER_PATH = './chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)


def log(message):
    print(f'[{datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]}]: {message}')


def download_content(file_name, source_link, extension):
    file_path = f'./files/products/{file_name}'
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
    file_path += f'/{file_name}.{extension}'

    # last_file_size = 0

    response = requests.get(source_link)
    # if os.path.isfile(file_path):
    #     last_file_size = os.path.getsize(file_path)

    # if len(response.content) > last_file_size:
    with open(file_path, 'wb') as prod_file:
        prod_file.write(response.content)
        prod_file.close()

    log(f">> Downloaded {file_name}.{extension}")
    # else:
    #     log(f">> Already Found {file_name}.{extension}")


def create_gewiss_json(file_name, features):
    file_path = f'./files/products/{file_name}'
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
    file_path += f'/info.json'

    default_val = {}

    if os.path.isfile(file_path):
        with open(file_path) as f:
            default_val = json.load(f)

    for (key, value) in features.items():
        default_val[key] = value

    with open(file_path, 'w') as f:
        json.dump(default_val, f)

    log(f">> Created JSON for {file_name}")


def scrape_content(prod_name, prod_link):
    is_image_present, is_pdf_present, is_desc_present = False, False, False
    driver.get(prod_link)

    image_css_sel = '#prodotto_dettaglio > div.container > div > div.first > div.gallery > ' \
                    'ul > div > div > li > a'
    pdf_css_sel = '#productDescription > div.download_box > div.downloadprodotto.datitecnici.' \
                  'anonymous > ul:nth-child(1) > li:nth-child(2) > a'
    description_css_sel = '#prodotto_dettaglio > div.container > div > div.first > div.contentwrap > h3'
    try:
        driver_wait = WebDriverWait(driver, 5)
        driver_wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, image_css_sel)))
        driver_wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, pdf_css_sel)))
        driver_wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, description_css_sel)))
    except Exception as e:
        log(f"Error in {prod_name} : {repr(e)}")

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    image = soup.select_one(image_css_sel)
    if image is not None:
        is_image_present = True
        image_href = image['href']
        image_url = 'https://www.gewiss.com' + image_href
        threading.Thread(target=download_content, args=(prod_name, image_url, 'jpg')).start()

    pdf = soup.select_one(pdf_css_sel)
    if pdf is not None:
        is_pdf_present = True
        pdf_href = pdf['href']
        pdf_url = 'https://www.gewiss.com' + pdf_href
        threading.Thread(target=download_content, args=(prod_name, pdf_url, 'pdf')).start()

    description = soup.select_one(description_css_sel)
    if description is not None:
        is_pdf_present = True
        threading.Thread(target=create_gewiss_json, args=(prod_name, {
            'description': description.text
        })).start()

    return is_image_present, is_pdf_present, is_desc_present


def main():
    try:
        with open('files/product_list_with_links.csv') as in_file:
            with open('files/product_list_with_links_with_state.csv', 'w') as out_file:
                reader = csv.reader(in_file)
                writer = csv.writer(out_file)
                writer.writerow(['product_model', 'product_link', 'image_found', 'pdf_found', 'desc_found'])
                for row in reader:
                    product_name = row[0]
                    product_link = row[1]
                    log(f"Working on {product_name}")
                    if product_link != "":
                        image_state, pdf_state, desc_state = scrape_content(product_name, product_link)
                        row.append(str(image_state))
                        row.append(str(pdf_state))
                        row.append(str(desc_state))
                    else:
                        log(">> But Not Found")
                        row.append(str(False))
                        row.append(str(False))
                        row.append(str(False))
                    writer.writerow(row)
    except Exception as e:
        log(f"Error: {repr(e)}")
    finally:
        driver.close()


if __name__ == '__main__':
    main()
