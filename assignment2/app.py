from flask import Flask, escape, request, Blueprint

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
    return "createTest"

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
    return "upload"

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
    return "tests"

if __name__ == '__main__':
    app.run()