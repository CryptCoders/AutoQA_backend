from flask import jsonify, request
from flask_restful import Resource
from utils.get_question_answer import get_qa
from utils.extract_text import extract
from utils.video import extract_from_video

class GenerateQuestionAnswer(Resource):
    @staticmethod
    def post(num_questions):
        file = request.files.get('file')
        text = ""

        if file.filename.split('.')[1] == 'pdf':
            text = extract(file)
        else:
            text = extract_from_video(file)

        questions_and_answers = []
        for page_text in text:
            questions_and_answers.extend(get_qa(page_text, num_questions))

        for qa_pair in questions_and_answers:
            if type(qa_pair['answer']) == list:
                qa_pair['type'] = 'mcq'
            else:
                qa_pair['type'] = 'sentence'

        return jsonify({'data': questions_and_answers})