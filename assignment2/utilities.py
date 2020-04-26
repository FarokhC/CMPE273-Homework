import sqlite3
import traceback
import json
import pickle

DATABASE_FILE = './exam.db'

#Adds an exam/test and its answer key to the database
def add_test_in_db(subject, answer_key):
    #Create table in DB if it does not exist
    try :
        conn = sqlite3.connect(DATABASE_FILE)
        # create_table_query = 'CREATE TABLE IF NOT EXISTS test_data (column1 INTEGER test_id PRIMARY KEY, column2 TEXT subject, column3 TEXT answer_key, column4 TEXT submisisons)'
        create_table_query = 'CREATE TABLE IF NOT EXISTS TEST_DATA(test_id INTEGER PRIMARY KEY, subject TEXT NOT NULL UNIQUE, answer_key TEXT NOT NULL, submissions TEXT);'

        conn.execute(create_table_query)
    except Exception as e:
        raise Exception("Could not create database table: " + str(e))

    #Write to DB
    try:
        submissions = []
        cur = conn.cursor()
        cur.execute("PRAGMA table_info({})".format("TEST_DATA"))
        print("table data: " + str(cur.fetchall()))
        write_query = 'INSERT OR REPLACE INTO TEST_DATA (subject, answer_key, submissions) VALUES (\'{}\', \'{}\', \'{}\');'.format(str(subject), str(answer_key), str(submissions))
        print("Write Query: " + str(write_query))
        conn.execute(write_query)
    except Exception as e:
        raise Exception("Could not write to database: " + str(e))

    #Retrieve test_id
    try:
        get_latest_test_id_query = "SELECT last_insert_rowid();"
        test_id = conn.execute(get_latest_test_id_query).fetchall()[0][0]
        print ("test ID: " + str(test_id))

        get_database_contents(conn)

    except Exception as e:
        raise Exception("Could not get test_id: " + str(e))

    #commit changes and close connection
    try:
        conn.commit()
        conn.close()
    except Exception as e:
        raise Exception("Could not commit or close connection for adding test: " + str(e))

    return {
        'test_id': test_id,
        'subject': subject,
        'answer_key': answer_key,
        'submissions': submissions
    }

#Retrieves database contents
def get_database_contents(conn):
        select_all_query = "SELECT * from TEST_DATA"
        res = conn.execute(select_all_query).fetchall()
        print ("database " + str(res))

#Compares the scantron to the answer key
def test_scantron(id, file_location, name, subject, scantron_data, scantron_url):
    submission_result = {}
    try:
        conn = sqlite3.connect(DATABASE_FILE)

        select_all_query = "SELECT * from TEST_DATA"
        res = conn.execute(select_all_query).fetchall()
        print ("database " + str(res))

        answer_key_query = 'SELECT * FROM TEST_DATA WHERE subject = \'{}\''.format(subject)
        answer_key = conn.execute(answer_key_query).fetchall()[0][2]
        print ("answer_key: " + str(answer_key))

        res = get_scantron_results(file_location, scantron_data, answer_key, id, subject, name, scantron_url)

        submission_result['scantron_id'] = id
        submission_result['scantron_url'] = res['scantron_url']
        submission_result['name'] = name
        submission_result['subject'] = subject
        submission_result['score'] = res['score']
        submission_result['result'] = res['result']

        write_result_to_db(conn, submission_result)

    except Exception as e:
        raise Exception("Could not add scantron to database: " + str(e))

    try:
        conn.commit()
        conn.close()

    except Exception as e:
        raise Exception("Could not commit or close connection for test scantron data: " + str(e))

    return submission_result

#Retreives and returns the scantron test results
def get_scantron_results(file_location, scantron_data, answer_key, test_id, subject, name, scantron_url):
    try:
        exam_data = None
        with open(file_location, 'r') as file:
            exam_data = file.read()
        conn = sqlite3.connect(DATABASE_FILE)
        answer_key_query = 'SELECT * FROM TEST_DATA WHERE subject = \'{}\''.format(subject)
        answer_key = conn.execute(answer_key_query).fetchall()[0][2]
        answer_key_json = json.loads(answer_key)
        answer_key_set = answer_key_json.keys()
        exam_data_json = json.loads(exam_data)
        exam_data_json = exam_data_json['answers']
        exam_data_keys = exam_data_json.keys()
        score = 0
        exam_comparison = {}
        if set(answer_key_set) != set(exam_data_keys):
            raise Exception("Scantron question numbers do not match answer key question numbers")
        else:
            for key in set(answer_key_set):
                res = {}
                if(exam_data_json[key] == answer_key_json[key]):
                    score = score + 1
                res["actual"] = exam_data_json[key]
                res["expected"] = answer_key_json[key]
                exam_comparison[key] = res
        submission_result = {}
        submission_result['scantron_id'] = test_id
        submission_result['scantron_url'] = scantron_url
        submission_result['name'] = name
        submission_result['subject'] = subject
        submission_result['score'] = score
        submission_result['result'] = exam_comparison
        write_result_to_db(conn, submission_result)
        conn.close()
        return submission_result

    except Exception as e:
        raise Exception("Failed to get results: " + str(e))

def write_result_to_db(conn, result):
    try:
        read_result_query = 'SELECT * FROM TEST_DATA WHERE subject = \'{}\''.format(result['subject'])
        res = conn.execute(read_result_query).fetchall()
        print("res: " + str(res))
        submission_array = res[0][3]
        # submission_array = submission_array.replace('\'' ,'\"').replace('\\', '')

        submission_array = json.loads(submission_array.replace('\'', '\"'))
        print("Old submission array: " + str(submission_array))
        #TODO: Handle case where the user tests same scantron multiple times
        submission_array.append(result)
        submission_array = json.dumps(submission_array).replace('\"', '\'')
        # submission_array = json.dumps(submission_array)

        print("Submission_array: " + str(submission_array))
        submission_array.encode('utf-8')
        write_result_query = 'UPDATE TEST_DATA SET submissions = \"{}\" WHERE subject = \"{}\"'.format(submission_array, result['subject'])

        print("Write result query: " + str(write_result_query))
        conn.execute(write_result_query)
        conn.commit()

        get_database_contents(conn)

    except Exception as e:
        raise Exception("Could not write submission result to db: " + str(e))

#Returns all of the scantron results for a certain test id
def get_all_scantron_results(test_id):
        conn = sqlite3.connect(DATABASE_FILE)
        get_database_contents(conn)
        read_result_query = 'SELECT * FROM TEST_DATA WHERE test_id = {}'.format(test_id)
        res = conn.execute(read_result_query).fetchall()

        ret = {}
        try:
            ret['test_id'] = res[0][0]
            ret['subject'] = res[0][1]
            ret['answer_keys'] = res[0][2]
            ret['submissions'] = res[0][3]
        except Exception as e:
            raise Exception("The test id does not exist: " + str(e))

        return ret
