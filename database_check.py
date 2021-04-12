import sqlite3
import pandas as pd

PATH_TO_DB = './'
conn = sqlite3.connect(PATH_TO_DB + 'tiki_data_minh.db')

query = '''

SELECT *
FROM products
    WHERE Review >= 1000
    ORDER BY Review+0 DESC
    LIMIT 10

'''

pd.set_option('display.max_columns',None)
pd.set_option('max_colwidth',40)
df = pd.read_sql_query(query, conn)
print(df)
conn.close()
