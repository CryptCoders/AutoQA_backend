from flask import jsonify, request
from flask_restful import Resource
from collections import ChainMap
from utils.extract_text import extract
from utils.help import generateQA
from dotenv import dotenv_values
from utils.video import extract_from_video

N = int(dotenv_values('.env')['N'])

class GenerateBriefAnswer(Resource):
    @staticmethod
    def post(level):
        file = request.files.get('file')

        text = ""

        if file.filename.split('.')[1] == 'pdf':
            for page_text in extract(file):
                text += page_text
        else:
            text = extract_from_video(file)

        questions_and_answers = dict(ChainMap(*[generateQA(text[i:min(len(text), i + N)], level) for i in range(0, len(text), N)]))
        # questions_and_answers = generateQA(text, level)

        return jsonify({'data': questions_and_answers})