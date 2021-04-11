import sqlite3
import pandas as pd

PATH_TO_DB = './'
#conn = sqlite3.connect(PATH_TO_DB + 'tiki_data_minh.db')
conn = sqlite3.connect(PATH_TO_DB + 'tiki_data_steph.db')


query = '''

SELECT *
FROM categories

'''

df = pd.read_sql_query(query, conn)
print(df)


query = '''

SELECT *
FROM products

'''

df = pd.read_sql_query(query, conn)
print(df)
