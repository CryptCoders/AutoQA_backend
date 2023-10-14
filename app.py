from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import extract_text
import get_question_answer

app = Flask(__name__)
api = Api(app)

class GenerateQuestionAnswer(Resource):
    def post(self, num_questions):
        file = request.files.get('file')
        text = extract_text.extract(file)
        questions_and_answers = get_question_answer.get_qa(text, num_questions)

        for qa_pair in questions_and_answers:
            if type(qa_pair['answer']) == list:
                qa_pair['type'] = 'mcq'
            else:
                qa_pair['type'] = 'sentence'

        return jsonify({'data': questions_and_answers})

api.add_resource(GenerateQuestionAnswer, '/generate-question-answer/<int:num_questions>')

if __name__ == '__main__':
    app.run(debug = True)