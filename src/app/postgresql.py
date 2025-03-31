import psycopg2

conn = psycopg2.connect(database="db_name",
                        host="db_host",
                        user="db_user",
                        password="db_pass",
                        port="db_port")

cursor = conn.cursor()

cursor.execute("SELECT * FROM DB_table WHERE id = 1")

# outputs only first line of result
print(cursor.fetchone())

# outputs all lines of result
print(cursor.fetchall())

# ouputs first 3 lines ouf result
print(cursor.fetchmany(size=3))

# close connection
conn.close()