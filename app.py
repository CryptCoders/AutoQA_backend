from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from controllers.generateQuestionAnswers import GenerateQuestionAnswers

app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(GenerateQuestionAnswers, '/generate-question-answers/<string:bloom_level>')

if __name__ == '__main__':
    app.run(debug = True)