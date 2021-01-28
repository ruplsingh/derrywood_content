import json
import pathlib
import requests
import threading


def download_content(file_name, file, source_link, extension):
    file_path = f'./files/products/{file_name}'
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
    file_path += f'/{file}.{extension}'

    response = requests.get(source_link)
    with open(file_path, 'wb') as prod_file:
        prod_file.write(response.content)
        prod_file.close()

    print(f">> Downloaded {file_name}.{extension}")


vinpower_products = json.load(open('files/vinpower_products.json'))
new_products = []

for product in vinpower_products:
    name = str(product['Name'])
    short_desc = product['Short description']
    names = name.split('-')
    if len(names) > 1:
        product['Name'] = ''.join(str(names[0]).strip().split())
        product['Short description'] = ''.join(names[1:]) + "\n" + short_desc

    name = str(product['Name'])
    count = 1
    for item in product['Images'].split(","):
        threading.Thread(target=download_content,
                         args=(name, f"{name}-{count}", item.strip(), item.strip()[-3:])).start()
        count += 1
    new_products.append(product)
    print(product)

open('files/vinpower_new_products.json', 'w').write(json.dumps(new_products))
