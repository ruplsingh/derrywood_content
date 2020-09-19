import csv
import requests
import pathlib
import threading
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

    response = requests.get(source_link)
    prod_image = open(file_path, 'wb')
    prod_image.write(response.content)
    prod_image.close()
    log(f">> Downloaded {file_name}.{extension}")


def scrape_content(prod_name, prod_link):
    is_image_present, is_pdf_present = False, False
    driver.get(prod_link)

    image_css_sel = '#prodotto_dettaglio > div.container > div > div.first > div.gallery > ' \
                    'ul > div > div > li > a'
    pdf_css_sel = '#productDescription > div.download_box > div.downloadprodotto.datitecnici.' \
                  'anonymous > ul:nth-child(1) > li:nth-child(2) > a'
    try:
        driver_wait = WebDriverWait(driver, 5)
        driver_wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, image_css_sel)))
        driver_wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, pdf_css_sel)))
    except Exception as e:
        log(f"Error {repr(e)}")

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

    return is_image_present, is_pdf_present


def main():
    try:
        in_file = open('files/product_list_with_links.csv')
        out_file = open('files/product_list_with_links_with_state.csv', 'w')
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)
        writer.writerow(['product_model', 'product_link', 'image_found', 'pdf_found'])
        for row in reader:
            product_name = row[0]
            product_link = row[1]
            log(f"Working on {product_name}")
            if product_link != "":
                image_state, pdf_state = scrape_content(product_name, product_link)
                row.append(str(image_state))
                row.append(str(pdf_state))
            else:
                log(">> But Not Found")
                row.append(str(False))
                row.append(str(False))
            writer.writerow(row)
    except Exception as e:
        log(f"Error: {repr(e)}")
    finally:
        driver.close()


if __name__ == '__main__':
    main()
