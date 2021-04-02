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

for item in csv.DictReader(open('files/derrywood_db_filled.csv', encoding='utf-8-sig'), delimiter=','):
    item_id = item['id']
    status = item['status']
    is_featured = item['is_featured']
    iebg_price = item['iebg price']
    kellihers_price = item['kellihers price']
    independence_price = item['independence price']
    ewl_price = item['EWL price']

    print(item_id, status, is_featured, iebg_price, kellihers_price, independence_price, ewl_price)

    execute_query(mydb,
                  f"UPDATE products SET status = '{status}', is_featured = {is_featured}"
                  f" WHERE id = {item_id}")

    execute_query(mydb,
                  f"INSERT INTO group_product VALUES (2, {item_id}, {iebg_price})")
    execute_query(mydb,
                  f"INSERT INTO group_product VALUES (3, {item_id}, {kellihers_price})")
    execute_query(mydb,
                  f"INSERT INTO group_product VALUES (4, {item_id}, {independence_price})")
    execute_query(mydb,
                  f"INSERT INTO group_product VALUES (5, {item_id}, {ewl_price})")
