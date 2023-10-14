from question_answering import QuestionGenerator

def get_qa(text, questions):
    qg = QuestionGenerator()

    qa_list = qg.generate(
        text,
        num_questions=questions,
        answer_style="all",
        use_evaluator=True
    )

    return qa_list
