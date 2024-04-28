import google.generativeai as genai
import json
from xmltodict import parse
import re

def correctFormat(xml_string):
    xml_arr = xml_string.split("\n")
    while "</questions>" not in xml_arr[-1] and "</question-answer>" not in xml_arr[-1]:
        xml_arr.pop()

    if "</questions>" not in xml_arr[-1]:
        xml_arr.append("</questions>")

    return "\n".join(xml_arr)

def generateQA(pdf_text, number):
    genai.configure(api_key="AIzaSyAiIh4uO1L9EcD-jqb4D9cn6BwggbcZwwM")

    generation_config = {
        "temperature": 0.5,
        "top_p": 1,
        "top_k": 1,
        # "max_output_tokens": 2048,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro", generation_config=generation_config, safety_settings=safety_settings)
    convo = model.start_chat(history=[])

    prompt = ""

    if number == 1:
        prompt =  "Create xml that contains 20 question-answer pairs with one line answers and conatins keys 'question' for question and 'answer' for answer from the above text. Please provide questions and one line answers in xml format only." + '''Keep following format
        <questions>
          <question-answer>
            <question></question>
            <answer></answer>
          </question-answer>
        </questions>'''

    elif number == 2:
        prompt = "Create xml that contains 5 question-answer pairs with long answers and conatins keys 'question' for question and 'answer' for answer from the above text. Please provide questions and long answers in xml format only." + '''Keep following format
        <questions>
          <question-answer>
            <question></question>
            <answer></answer>
          </question-answer>
        </questions>'''

    elif number == 3:
        prompt = "Create xml that contains 20 question-answer pairs with multiple choice answers and conatins keys 'question' for question, 'option' for option and 'answer' for answer from the above text. Please provide questions and multiple choice answers in xml format only." + '''Keep following format
        <questions>
          <question-answer>
            <question></question>
            <option></option>
            <option></option>
            <option></option>
            <option></option>
            <answer></answer>
          </question-answer>
        </questions>'''

    prompt += pdf_text
    convo.send_message(prompt)
    # print(convo.last.text)
    response = convo.last.text
    # print(response)
    response = re.sub(r"```xml", "", response)
    response = re.sub(r"```", "", response)
    response = correctFormat(response)

    return parse(response)