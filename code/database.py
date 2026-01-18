import pypyodbc
import pandas as pd

from datetime import datetime
from datetime import timedelta


def connect_db(DATABASE_DIR,  *,PWD=None):
    ''' connect to the database
    '''
    conn = None
    try:
        connection = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;PWD=%s'%(DATABASE_DIR,PWD)
        conn = pypyodbc.connect(connection)
        cursor =  conn.cursor()
    except:
        return False, False
        print(f'>> cannot connect with the database. Bye~')

    return conn, cursor

def fetch_db(DATABASE_DIR, table, *,  PWD=None ):
    ''' A function to pull out a column from  a table in the db
        DATABASE_DIR = database location
        table = name of the table
        column = name of the column'''

    conn, cursor = connect_db(DATABASE_DIR )

    if conn == False:
        col_lt = False
    else:
        col = cursor.execute(f'SELECT * FROM [{table}]')
        rows = col.fetchall()
        columns = [column[0] for column in col.description]   # Extract column names

        df = pd.DataFrame.from_records(rows, columns=columns)

    return df
