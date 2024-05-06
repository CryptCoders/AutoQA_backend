import os, queue, threading
from flask import jsonify, request
from flask_restful import Resource
from utils.generateQuestions import generateQuestions
from utils.generateAnswers import generateAnswer

class GenerateQuestionAnswers(Resource):
    @staticmethod
    def post(bloom_level):
        file = request.files.get('file')
        file.save('temp.pdf')

        file_content, questions = generateQuestions('temp.pdf')
        api_keys = os.getenv("GOOGLE_API_KEYS").split(',')

        response = []

        api_queue = queue.Queue()
        for api_key in api_keys:
            api_queue.put(api_key)

        keys_lock = threading.Lock()

        def multithreading(question):
            api_key = None

            with keys_lock:
                while api_queue.empty():
                    pass

                api_key = api_queue.get(block = True)
                answer = generateAnswer(file_content, question, api_key)

                with keys_lock:
                    api_queue.put(api_key)

                return answer

        threads = []

        for question in questions:
            thread = threading.Thread(target = lambda q=question: response.append({
                "question": q,
                "answer": multithreading(q)
            }))

            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return jsonify({ 'data': response })