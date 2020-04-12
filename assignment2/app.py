from flask import Flask, escape, request, Blueprint
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
        return 500

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
    scantron_data = request.args.get('BINARY_SCANTRON_PDF_FILE_DATA')

    #Do logic to upload scantron here

    response  = {}
    response['scantron_id'] = 1
    response['scantron_url'] = 1
    response['name'] = 1
    response['subject'] = 1
    response['score'] = 1
    response['result'] = 1

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

    response  = {}
    response['test_id'] = id
    response['subject'] = "subject"
    response['answer_keys'] = {}
    response['submissions'] = []

    return response

if __name__ == '__main__':
    app.run()