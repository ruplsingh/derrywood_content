import csv
import mysql.connector


def execute_query(mydb, query):
    mycursor = mydb.cursor()
    mycursor.execute(query)
    mydb.commit()


def select_query(mydb, query):
    mycursor = mydb.cursor()
    mycursor.execute(query)
    myresult = mycursor.fetchall()
    return myresult


mydb = mysql.connector.connect(
    host="derrywood.com",
    database="derrywoo_dwonline",
    user="derrywoo_dwonlineuser",
    password="billy@derrywood",
)

with open('files/pricelist_not_present.csv', 'w') as out_file:
    writer = csv.writer(out_file)
    writer.writerow(['name'])
    execute_query(mydb,
                  "UPDATE group_product SET price = 0.0")

    for item in csv.DictReader(open('files/initial_pricelist_gw.csv', encoding='utf-8-sig'), delimiter=','):
        name = f"GW{item['name']}"
        price = item['price']
        result = select_query(mydb, f"SELECT id FROM products WHERE title = '{name}'")
        if len(result) > 0:
            product_id = result[0][0]
            execute_query(mydb,
                          f"UPDATE group_product SET price = {price} where product_id = {product_id} and group_id = 1")
            print(f"Updated price of {name} to {price}")
        else:
            writer.writerow([name])

    for item in csv.DictReader(open('files/initial_pricelist.csv', encoding='utf-8-sig'), delimiter=','):
        name = item['name']
        price = item['price']
        result = select_query(mydb, f"SELECT id FROM products WHERE title = '{name}'")
        if len(result) > 0:
            product_id = result[0][0]
            execute_query(mydb,
                          f"UPDATE group_product SET price = {price} where product_id = {product_id} and group_id = 1")
            print(f"Updated price of {name} to {price}")
        else:
            writer.writerow([name])
