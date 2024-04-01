from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from controllers.generateQuestionAnswer import GenerateQuestionAnswer
from controllers.generateBriefAnswer import GenerateBriefAnswer
from dotenv import load_dotenv

load_dotenv('.env')

app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(GenerateQuestionAnswer, '/generate-question-answer/<int:num_questions>')
api.add_resource(GenerateBriefAnswer, '/generate-brief-answer/<int:level>')

if __name__ == '__main__':
    app.run(debug = True)