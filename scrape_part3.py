import os
import csv
import json
import pathlib
import requests
import threading
from datetime import datetime


def log(message):
    print(f'[{datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]}]: {message}')


def download_content(file_name, file, source_link, extension):
    file_path = f'./files/products/{file_name}'
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
    file_path += f'/{file}.{extension}'

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


def main():
    try:
        with open('files/product_wordpress.csv') as in_file:
            with open('files/product_wordpress_cleaned.csv', 'w') as out_file:
                reader = csv.reader(in_file)
                writer = csv.writer(out_file)
                writer.writerow(['product_model', 'product_link', 'image_found', 'pdf_found', 'desc_found'])
                for row in reader:
                    name = row[3].upper()
                    desc = row[8]
                    category = row[26]
                    tags = row[27]
                    images = row[29]

                    if name == "NAME" or name == "":
                        continue

                    threading.Thread(target=create_gewiss_json, args=(name, {
                        'category': category,
                        'tags': tags
                    })).start()
                    count = 1
                    for item in images.split(","):
                        threading.Thread(target=download_content,
                                         args=(name, f"{name}-{count}", item.strip(), item.strip()[-3:])).start()
                        count += 1
    except Exception as e:
        log(f"Error: {repr(e)}")


if __name__ == '__main__':
    main()
