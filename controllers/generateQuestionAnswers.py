import os
import queue
import threading
from flask import jsonify, request
from flask_restful import Resource
from utils.generateQuestions import generateQuestions
from utils.generateAnswers import generateAnswer
from utils.video import extract_from_video
from utils.ocr import extract_text_from_pdf

class GenerateQuestionAnswers(Resource):
    @staticmethod
    def post(bloom_level, ocr):
        file = request.files.get('file')
        filename = file.filename.lower()

        extracted_content = 'temp.pdf'

        if filename.endswith(('.pdf')):
            if not ocr:
                file.save('temp.pdf')
            else:
                extracted_content = extract_text_from_pdf('temp.pdf')
        else:
            extracted_content = extract_from_video(file)

        file_content, questions = generateQuestions(extracted_content, bloom_level.upper(), ocr)
        api_keys = os.getenv("GOOGLE_API_KEYS").split(',')

        response = []
        api_queue = queue.Queue()

        # Populate the API queue with available keys
        for api_key in api_keys:
            api_queue.put(api_key)

        def process_question(question):
            while True:
                try:
                    # Get an API key from the queue (blocking until available)
                    api_key = api_queue.get(block=True)

                    # Generate answer using the acquired API key
                    answer, keywords = generateAnswer(file_content, question, api_key)
                    print("Question :\n",question)
                    print("Answer :\n",answer)
                    print("Keywords :\n",keywords.split('\n'))
                    # Append the question-answer pair to the response list
                    response.append({
                        "question": question,
                        "answer": answer,
                        "keywords": keywords.split('\n')
                    })

                    # Mark the API key as available again by putting it back into the queue
                    api_queue.put(api_key)
                    break  # Exit the loop if answer is generated successfully
                except Exception as e:
                    # Handle exceptions (e.g., API errors) gracefully
                    print(f"Error processing question '{question}': {e}")
                    break  # Exit the loop on error

        # List to hold thread objects
        threads = []

        # Create and start a thread for each question
        for question in questions:
            thread = threading.Thread(target=process_question, args=(question,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Return the response as JSON
        return jsonify({ 'data': response })
