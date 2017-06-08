from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

con = connect(dbname='postgres',
              user='catalog',
              host='localhost',
              password='superman1$')

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = con.cursor()

cur.execute("DROP DATABASE IF EXISTS catalog")
cur.execute("CREATE DATABASE catalog")

cur.close()
con.close()
