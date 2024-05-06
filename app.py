from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import dotenv

from controllers.generateQuestionAnswers import GenerateQuestionAnswers

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(GenerateQuestionAnswers, '/generate-question-answers/<string:bloom_level>')
# api.add_resource(EvaluateAnswers, '/evaluate-answer')

if __name__ == '__main__':
    app.run(debug = True)