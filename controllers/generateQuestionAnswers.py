import os
import queue
import threading
from flask import jsonify, request
from flask_restful import Resource
from utils.generateQuestions import generateQuestions
from utils.generateAnswers import generateAnswer
from utils.video import extract_from_video

class GenerateQuestionAnswers(Resource):
    @staticmethod
    def post(bloom_level):
        file = request.files.get('file')
        filename = file.filename.lower()
        if filename.endswith(('.pdf')):
            
            file.save('temp.pdf')
        else:
            # Handle other file types (video)
            extracted_content = extract_from_video(file)
            

        file_content, questions = generateQuestions('temp.pdf', bloom_level.upper())
        api_keys = os.getenv("GOOGLE_API_KEYS").split(',')

        response = []
        api_queue = queue.Queue()

        # Populate the API queue with available keys
        for api_key in api_keys:
            print(api_key)
            api_queue.put(api_key)

        def process_question(question):
            while True:
                try:
                    # Get an API key from the queue (blocking until available)
                    api_key = api_queue.get(block=True)

                    # Generate answer using the acquired API key
                    answer = generateAnswer(file_content, question, api_key)
                    print("Question :\n",question)
                    print("Answer :\n",answer)
                    # Append the question-answer pair to the response list
                    response.append({
                        "question": question,
                        "answer": answer
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
        return jsonify({'data': response})
