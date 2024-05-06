import threading, os
from flask import jsonify, request
from flask_restful import Resource
from utils.generateQuestions import generateQuestions
from utils.generateAnswers import generateAnswer
from collections import deque

class GenerateQuestionAnswers(Resource):
    @staticmethod
    def post(bloom_level):
        file = request.files.get('file')
        file.save('temp.pdf')

        file_content, questions = generateQuestions('temp.pdf')
        api_keys = deque(os.getenv("GOOGLE_API_KEYS").split(','))

        response = []

        for question in questions:
            api_keys.append(api_keys[0])
            answer = generateAnswer(file_content, question, api_keys.popleft())

            response.append({
                "question": question,
                "answer": answer
            })

        return jsonify({ 'data': response })