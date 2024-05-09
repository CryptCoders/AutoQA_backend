from langchain_google_genai import GoogleGenerativeAI
from langchain.evaluation import load_evaluator

import os
api_key = os.getenv("GOOGLE_API_QUESTION_KEY")

scoring_criteria = """
    "Score Scale: 1-10

    Criteria:

    Accuracy: How well does the response correspond to factual information? (Weight: 0.6)
    Relevance: Does the response directly address the prompt or question? (Weight: 0.4)
    Completeness: Does the answer provide all necessary details? (Weight: 0.0)

    Based on how much the relevance of the prediction give score:

    Score 0-1: The prediction is completely unrelated to the reference.
    Score 2-4: The prediction has minor relevance but does not align with the reference.
    Score 5-7: The prediction has moderate relevance but contains inaccuracies.
    Score 8-9: The prediction aligns with the reference but has minor errors.
    Score 10: The prediction is completely and exactly aligns perfectly with the reference.
"""

def loadLLM():
    llm = GoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key
    )

    return llm

def llm_pipeline(question, desired_answer, user_answer):
    llm_evaluate_pipeline = loadLLM()
    evaluator = load_evaluator("labeled_score_string", criteria = scoring_criteria, llm = llm_evaluate_pipeline)

    score = evaluator.evaluate_strings(
        prediction = user_answer,
        reference = desired_answer,
        input = question
    )

    print(score)
    return score

def evaluate(question, desired_answer, user_answer):
    score = llm_pipeline(question, desired_answer, user_answer)
    return score['score']

if __name__ == '__main__':
    evaluate(
        "Explain the primary purpose of a computer network",
        """	
            The primary purpose of a computer network is to facilitate communication and resource sharing among multiple devices connected to it. By establishing connections between devices, networks enable the exchange of data, access to shared resources, and collaboration among users. Networks allow devices to communicate and share resources regardless of their physical location or the type of device they are using.
        """,
        """	
            The primary purpose of a computer network is to facilitate communication and resource sharing among multiple devices connected to it. By establishing connections between devices, networks enable the exchange of data, access to shared resources, and collaboration among users. Networks allow devices to communicate and share resources regardless of their physical location or the type of device they are using.
        """
    )