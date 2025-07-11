import mysql.connector

conn = mysql.connector.connect(
    host='atlantareciclajes.mysql.pythonanywhere-services.com',
    user='atlantareciclaje',
    password='TU_PASSWORD_AQUI',
    database='atlantareciclaje$default'
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES;")

print("Tablas encontradas:")
for table in cursor.fetchall():
    print(table)

conn.close()
