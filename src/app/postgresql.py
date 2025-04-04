import psycopg2 as ps
import os
from dotenv import load_dotenv
from logger import Logger

load_dotenv()

log = Logger().getLogger()

def get_postgress_conn():
    DATABASE = os.getenv("DB_NAME")
    HOST = os.getenv("DB_HOST")
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASS")
    PORT = os.getenv("DB_PORT")
    
    try:
        return ps.connect(database=DATABASE,
                                host=HOST,
                                user=USER,
                                password=PASSWORD,
                                port=PORT)
    except ps.OperationalError as e:
        # log e
        log.error("creating connection to the postgresql DB failed. Error: \n" + str(e))
        return None

def create_table(conn):
    if conn is None:
        log.error("Creating users table failed. Error: Connection to DB missing")
        return
    
    try:
        cursor = conn.cursor()
        Name = "users"
        create=f"""CREATE EXTENSION IF NOT EXISTS pgcrypto; CREATE TABLE IF NOT EXISTS {Name} (
            id INT GENERATED ALWAYS AS IDENTITY,
            user_name VARCHAR(255) NOT NULL, 
            password TEXT NOT NULL,
            deck_ids INTEGER[]
        )"""
        cursor.execute(create)
        conn.commit()
        log.info("Succesfully created users table")
    except Exception as e:
        log.error("Creating users table failed. Error: \n" + str(e))

def clean_table(conn, table_name: str):
    if conn is None:
        log.error("Cleaning users table failed. Error: Connection to DB missing")
        return
    
    cursor = conn.cursor()
    clean=f"TRUNCATE {table_name};"
    cursor.execute(clean)
    conn.commit()
    log.info("Succesfully cleaned users table")

def delete_table(conn, table_name):
    if conn is None:
        log.error("Deleting users table failed. Error: Connection to DB missing")
        return
    
    cursor = conn.cursor()
    clean=f"DROP TABLE IF EXISTS {table_name};"
    cursor.execute(clean)
    conn.commit()
    log.info("Succesfully deleted users table")

def user_with_crypt_pass(conn):
    if conn is None:
        log.error("Creating user failed. Error: Connection to DB missing")
        return
    
    sql = f""" INSERT INTO DB_TEST (user_name, password) VALUES (
            'tsuna',
            crypt('tsunapasswd', gen_salt('md5'))
        );
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    log.info("Succesfully added test-user tsuna")

def get_user_tst(conn, passwd):
    if conn is None:
        log.error("Receiving users from db failed. Error: Connection to DB missing")
        return
    
    sql = f""" SELECT id FROM DB_TEST
            WHERE user_name = 'tsuna' 
            AND password = crypt('{passwd}', password);
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    
    users = cursor.fetchall()
    
    conn.commit()
    return users