from langchain_google_genai import GoogleGenerativeAI
from langchain.evaluation import load_evaluator, EvaluatorType

import os
api_key = os.getenv("GOOGLE_API_QUESTION_KEY")

scoring_criteria = """
    "Score Scale: 1-10
    
    Criteria:
    
    Accuracy: How well does the response correspond to factual information? (Weight: 0.6)
    Relevance: Does the response directly address the prompt or question? (Weight: 0.3)
    Completeness: Does the answer provide all necessary details? (Weight: 0.1)
    
    1: Completely irrelevant or inaccurate
    2-3: Somewhat relevant but with significant inaccuracies
    4-6: Moderately relevant with minor inaccuracies or missing details
    7-8: Mostly relevant and accurate, with some room for improvement
    9-10: Perfect answer - highly relevant, accurate, complete, and informative
"""

def loadLLM():
    llm = GoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key
    )

    return llm

def llm_pipeline(question, desired_answer, user_answer):
    llm_evaluate_pipeline = loadLLM()
    evaluator = load_evaluator(evaluator = EvaluatorType.LABELED_SCORE_STRING, scoring_criteria = scoring_criteria, llm = llm_evaluate_pipeline)

    score = evaluator.evaluate_strings(
        prediction = user_answer,
        reference = desired_answer,
        input = question
    )

    return score

def evaluate(question, desired_answer, user_answer):
    score = llm_pipeline(question, desired_answer, user_answer)
    return score['score']