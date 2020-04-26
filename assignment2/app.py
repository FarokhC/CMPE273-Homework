from flask import Flask, escape, request, Blueprint, send_file
import os

import utilities

app = Flask(__name__)

"""
Request

POST http://localhost:5000/api/tests

{
    "subject": "Math",
    "answer_keys": {
        "1": "A",
        "2": "B",
        "3": "C",
        "..": "..",
        "49": "D",
        "50": "E"
    }
}
Response

201 Created

{
    "test_id": 1,
    "subject": "Math",
    "answer_keys": {
        "1": "A",
        "2": "B",
        "3": "C",
        "..": "..",
        "49": "D",
        "50": "E"
    },
    "submissions": []
}
"""
@app.route('/api/tests', methods = ["POST"])
def createTest():
    subject = request.args.get('subject')
    answer_key = request.args.get('answer_key')

    #Do logic to create tests here
    try:
        ret = utilities.add_test_in_db(subject, answer_key)
        response = {}
        response['test_id'] = ret['test_id']
        response['subject'] = ret['subject']
        response['answer_key'] = ret['answer_key']
        response['submissions'] = ret['submissions']

        return response, 201
    except Exception as e:
        print("Failed to create table or write to table: " + str(e))
        return str(e), 500

"""
Request

POST http://localhost:5000/api/tests/1/scantrons

# HTTP Request Body
BINARY_SCANTRON_PDF_FILE_DATA
Response

201 Created

{
    "scantron_id": 1,
    "scantron_url": "http://localhost:5000/files/1.pdf",
    "name": "Foo Bar",
    "subject": "Math",
    "score": 40,
    "result": {
        "1": {
            "actual": "A",
            "expected": "B"
        },
        "..": {
            "actual": "..",
            "expected": ".."
        },
        "50": {
            "actual": "E",
            "expected": "E"
        }
    }
}
"""
@app.route('/api/tests/<id>/scantrons', methods = ["POST"])
def uploadScantron(id):
    name = request.args.get('name')
    subject = request.args.get('subject')
    # scantron_data = request.args.get('BINARY_SCANTRON_PDF_FILE_DATA')
    scantron_data = request.files
    save_location = '/files/'
    scantron_url = "http://" + request.host + save_location
    abs_file_location = None
    try:
        json_file = request.files['file']
        scantron_url = scantron_url + json_file.filename
        abs_file_location = os.getcwd() + "/" + save_location + "/" + json_file.filename
        json_file.save(abs_file_location)

    except Exception as e:
        print("Failed to upload file: " + str(e))
    try:
    #Do logic to upload scantron here
        res = utilities.test_scantron(id, abs_file_location, name, subject, scantron_data, scantron_url)
    except Exception as e:
        return str(e), 500

    response  = {}
    response['scantron_id'] = id
    response['scantron_url'] = res['scantron_url']
    response['name'] = name
    response['subject'] = subject
    response['score'] = res['score']
    response['result'] = res['result']

    return response, 201

"""
Request

GET http://localhost:5000/api/tests/1

Response

{
    "test_id": 1,
    "subject": "Math",
    "answer_keys": {
        "1": "A",
        "2": "B",
        "3": "C",
        "..": "..",
        "49": "D",
        "50": "E"
    },
    "submissions": [
        {
            "scantron_id": 1,
            "scantron_url": "http://localhost:5000/files/1.pdf",
            "name": "Foo Bar",
            "subject": "Math",
            "score": 40,
            "result": {
                "1": {
                    "actual": "A",
                    "expected": "B"
                },
                "..": {
                    "actual": "..",
                    "expected": ".."
                },
                "50": {
                    "actual": "E",
                    "expected": "E"
                }
            }
        }
    ]
}
"""
@app.route('/api/tests/<id>', methods = ['GET'])
def checkAllScantrons(id):
    #Do logic to scan scantron here

    try:
        res = utilities.get_all_scantron_results(id)
    except Exception as e:
        return str(e), 500

    response  = {}
    response['test_id'] = res['test_id']
    response['subject'] = res['subject']
    response['answer_keys'] = res['answer_keys']
    response['submissions'] = res['submissions']

    return response

#Returns the file
@app.route('/<path:file_location>')
def dir_listing(file_location):
    file_path = os.path.join(os.getcwd(), file_location)

    if os.path.isfile(file_path):
        return send_file(file_path)

    else:
        return "Could not find file: " + str(file_path), 404

if __name__ == '__main__':
    app.run()