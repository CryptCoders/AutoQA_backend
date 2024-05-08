from flask import request, jsonify
from flask_restful import Resource

from utils.evaluateAnswer import evaluate

class EvaluateAnswers(Resource):
    @staticmethod
    def post():
        data = request.get_json()

        return jsonify({ 'score': evaluate(data['question'], data['desired_answer'], data['user_answer']) })