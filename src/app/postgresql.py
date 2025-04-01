import psycopg2 as ps
import os
from dotenv import load_dotenv

load_dotenv()

def get_postgress_conn():
    DATABASE = os.getenv("db_name")
    HOST = os.getenv("db_host")
    USER = os.getenv("db_user")
    PASSWORD = os.getenv("db_pass")
    PORT = os.getenv("db_port")
    
    try:
        conn = ps.connect(database=DATABASE,
                                host=HOST,
                                user=USER,
                                password=PASSWORD,
                                port=PORT)

        cursor = conn.cursor()

        #cursor.execute("SELECT * FROM DB_table WHERE id = 1")

        # outputs only first line of result
        #print(cursor.fetchone())

        # outputs all lines of result
        #print(cursor.fetchall())

        # ouputs first 3 lines ouf result
        #print(cursor.fetchmany(size=3))
    except ps.OperationalError as e:
        # log e
        return None

#conn = get_postgress_conn()
    # close connection
#conn.close()