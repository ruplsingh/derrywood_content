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

with open('files/derrywood_db.csv', 'w') as out_file:
    writer = csv.writer(out_file)
    groups = {}
    for item in select_query(mydb, "SELECT id, title FROM groups"):
        groups[item[0]] = item[1]
    groups_row = ['id', 'title', 'status', 'is_featured', 'brand', 'discount'] + [f"{str(v).lower()} price" for k, v in groups.items()]
    writer.writerow(groups_row)

    brands = {}
    for item in select_query(mydb, "SELECT id, title FROM brands"):
        brands[item[0]] = item[1]

    for item in select_query(mydb, "SELECT id, title, status, discount, is_featured, brand_id FROM products"):
        product = []
        product.append(item[0])
        product.append(item[1])
        product.append(item[2])
        product.append(item[4])
        product.append(brands[item[5]])
        product.append(item[3])
        for group_id, group_name in groups.items():
            result = select_query(mydb,
                                  f"SELECT price FROM group_product WHERE product_id = {item[0]} AND group_id = {group_id}")
            if len(result) > 0:
                product.append(result[0][0])
            else:
                product.append(0)

        writer.writerow(product)
