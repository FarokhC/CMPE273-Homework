import sqlite3
import traceback

DATABASE_FILE = './exam.db'

#Adds an exam/test and its answer key to the database
def add_test_in_db(subject, answer_key):
    #Create table in DB if it does not exist
    try :
        conn = sqlite3.connect(DATABASE_FILE)
        # create_table_query = 'CREATE TABLE IF NOT EXISTS test_data (column1 INTEGER test_id PRIMARY KEY, column2 TEXT subject, column3 TEXT answer_key, column4 TEXT submisisons)'
        create_table_query = 'CREATE TABLE IF NOT EXISTS TEST_DATA(test_id INTEGER PRIMARY KEY, subject TEXT NOT NULL, answer_key TEXT NOT NULL, submissions TEXT);'

        conn.execute(create_table_query)
    except Exception as e:
        raise Exception("Could not create database table: " + str(e))

    #Write to DB
    try:
        submissions = []
        cur = conn.cursor()
        cur.execute("PRAGMA table_info({})".format("TEST_DATA"))
        print("table data: " + str(cur.fetchall()))
        write_query = 'INSERT INTO TEST_DATA (subject, answer_key, submissions) VALUES (\'{}\', \'{}\', \'{}\');'.format(str(subject), str(answer_key), str(submissions))
        print("Write Query: " + str(write_query))
        conn.execute(write_query)
    except Exception as e:
        raise Exception("Could not write to database: " + str(e))

    #Retrieve test_id
    try:
        get_latest_test_id_query = "select last_insert_rowid();"
        test_id = conn.execute(get_latest_test_id_query).fetchall()[0][0]
        print ("test ID: " + str(test_id))

        select_all_query = "select * from TEST_DATA"
        res = conn.execute(select_all_query).fetchall()
        print ("database " + str(res))

    except Exception as e:
        raise Exception("Could not get test_id: " + str(e))

    #commit changes and close connection
    try:
        conn.commit()
        conn.close()
    except Exception as e:
        raise Exception("Could not commit or close connection: " + str(e))

    return {
        'test_id': test_id,
        'subject': subject,
        'answer_key': answer_key,
        'submissions': submissions
    }