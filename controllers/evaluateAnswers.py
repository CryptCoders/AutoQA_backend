from flask import request, jsonify
from flask_restful import Resource
from utils.evaluate import text_similarity

class EvaluateAnswers(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        string1, string2 = data['desired_answer'], data['user_answer']

        score = text_similarity(string1, string2)

        return jsonify({ 'score': int(score) })