import os
import csv
import json
import pathlib
from datetime import datetime


def log(message):
    print(f'[{datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]}]: {message}')


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

                    create_gewiss_json(name, {
                        'category': category,
                        'tags': tags
                    })
                    # product_name = row[0]
                    # product_link = row[1]
                    # log(f"Working on {product_name}")
                    # if product_link != "":
                    #     image_state, pdf_state, desc_state = scrape_content(product_name, product_link)
                    #     row.append(str(image_state))
                    #     row.append(str(pdf_state))
                    #     row.append(str(desc_state))
                    # else:
                    #     log(">> But Not Found")
                    #     row.append(str(False))
                    #     row.append(str(False))
                    #     row.append(str(False))
                    # writer.writerow(row)
    except Exception as e:
        log(f"Error: {repr(e)}")


if __name__ == '__main__':
    main()
