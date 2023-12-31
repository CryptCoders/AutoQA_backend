import en_core_web_sm
import json
import random
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification
from typing import Any, List, Mapping, Tuple

class QAEvaluator():
    def __init__(self):
        QAE_PRETRAINED = 'iarfmoose/bert-base-cased-qa-evaluator'
        self.SEQ_LENGTH = 512

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.qae_tokenizer = AutoTokenizer.from_pretrained(QAE_PRETRAINED)
        self.qae_model = AutoModelForSequenceClassification.from_pretrained(QAE_PRETRAINED)

        self.qae_model.to(self.device)
        self.qae_model.eval()

    def _encode_qa(self, question: str, answer: str) -> torch.tensor:
        correct_answer = ""

        if type(answer) is list:
            for a in answer:
                if a["correct"]:
                    correct_answer = a["answer"]
        else:
            correct_answer = answer

        return self.qae_tokenizer(
            text=question,
            text_pair=correct_answer,
            padding='max_length',
            max_length=self.SEQ_LENGTH,
            truncation=True,
            return_tensors='pt'
        )

    def encode_qa_pairs(self, questions: List[str], answers: List[str]) -> List[torch.tensor]:
        encoded_pairs = []

        for question, answer in zip(questions, answers):
            encoded_qa = self._encode_qa(question, answer)
            encoded_pairs.append(encoded_qa)

        return encoded_pairs

    @torch.no_grad()
    def _evaluate_qa(self, encoded_qa_pair: torch.tensor):
        output = self.qae_model(**encoded_qa_pair)
        return output[0][0][1]

    def get_scores(self, encoded_qa_pairs: List[torch.tensor]) -> List[float]:
        scores = {}

        for i in range(len(encoded_qa_pairs)):
            scores[i] = self._evaluate_qa(encoded_qa_pairs[i])

        return [k for k, v in sorted(scores.items(), key=lambda item : item[1], reverse=True)]

class QuestionGenerator:
    def __init__(self):
        QG_PRETRAINED = 'iarfmoose/t5-base-question-generator'
        self.ANSWER_TOKEN = '<answer>'
        self.CONTEXT_TOKEN = '<context>'
        self.SEQ_LENGTH = 512

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        additional_special_tokens = ["<extra_id_{}>".format(i) for i in range(100)]
        self.qg_tokenizer = AutoTokenizer.from_pretrained(QG_PRETRAINED, additional_special_tokens=additional_special_tokens, use_fast=False)
        self.qg_model = AutoModelForSeq2SeqLM.from_pretrained(QG_PRETRAINED)
        self.qg_model.to(self.device)
        self.qg_model.eval()

        self.qa_evaluator = QAEvaluator()

    def _split_into_segments(self, text):
        MAX_TOKENS = 490

        paragraphs = text.split("\n")
        tokenized_paragraphs = [self.qg_tokenizer(p)["input_ids"] for p in paragraphs if len(p)]

        segments = []

        while len(tokenized_paragraphs):
            segment = []

            while len(segment) < MAX_TOKENS and len(tokenized_paragraphs):
                paragraph = tokenized_paragraphs.pop(0)
                segment.extend(paragraph)

            segments.append(segment)

        return [self.qg_tokenizer.decode(s, skip_special_tokens=True) for s in segments]

    def _split_text(self, text) -> List[str]:
        MAX_SENTENCE_LEN = 128
        sentences = re.findall(".*?[.!\?]", text)
        cut_sentences = []

        for sentence in sentences:
            if len(sentence) > MAX_SENTENCE_LEN:
                cut_sentences.extend(re.split("[,;:)]", sentence))

        cut_sentences = [s for s in sentences if len(s.split(" ")) > 5]
        sentences = sentences + cut_sentences

        return list(set([s.strip(" ") for s in sentences]))

    def _prepare_qg_inputs(self, sentences: List[str], text: str) -> Tuple[List[str], List[str]]:
        inputs = []
        answers = []

        for sentence in sentences:
            qg_input = f"{self.ANSWER_TOKEN} {sentence} {self.CONTEXT_TOKEN} {text}"
            inputs.append(qg_input)
            answers.append(sentence)

        return inputs, answers

    def _get_MC_answers(self, correct_answer: Any, docs: Any) -> List[Mapping[str, Any]]:
        entities = []

        for doc in docs:
            entities.extend([{"text": e.text, "label_": e.label_} for e in doc.ents])

        entities_json = [json.dumps(kv) for kv in entities]
        pool = set(entities_json)
        num_choices = min(4, len(pool)) - 1

        final_choices = []
        correct_label = correct_answer.label_
        final_choices.append({"answer": correct_answer.text, "correct": True})
        pool.remove(json.dumps({"text": correct_answer.text, "label_": correct_answer.label_}))

        matches = [e for e in pool if correct_label in e]

        if len(matches) < num_choices:
            choices = matches
            pool = pool.difference(set(choices))
            choices.extend(random.sample(pool, num_choices - len(choices)))
        else:
            choices = random.sample(matches, num_choices)

        choices = [json.loads(s) for s in choices]

        for choice in choices:
            final_choices.append({"answer": choice["text"], "correct": False})

        random.shuffle(final_choices)
        return final_choices

    def _prepare_qg_inputs_MC(self, sentences: List[str]) -> Tuple[List[str], List[str]]:
        spacy_nlp = en_core_web_sm.load()
        docs = list(spacy_nlp.pipe(sentences, disable=["parser"]))

        inputs_from_text = []
        answers_from_text = []

        for doc, sentence in zip(docs, sentences):
            entities = doc.ents

            if entities:
                for entity in entities:
                    qg_input = f"{self.ANSWER_TOKEN} {entity} {self.CONTEXT_TOKEN} {sentence}"
                    answers = self._get_MC_answers(entity, docs)
                    inputs_from_text.append(qg_input)
                    answers_from_text.append(answers)

        return inputs_from_text, answers_from_text

    def generate_qg_inputs(self, text, answer_style) -> Tuple[List[str], List[str]]:
        VALID_ANSWER_STYLES = ['all', 'sentences', 'multiple_choice']

        if answer_style not in VALID_ANSWER_STYLES:
            raise ValueError("Invalid answer style {}. Please choice from {}".format(answer_style, VALID_ANSWER_STYLES))

        inputs = []
        answers = []

        if answer_style == "sentences" or answer_style == "all":
            segments = self._split_into_segments(text)

            for segment in segments:
                sentences = self._split_text(segment)
                prepped_inputs, prepped_answers = self._prepare_qg_inputs(sentences, segment)
                inputs.extend(prepped_inputs)
                answers.extend(prepped_answers)

        if answer_style == "multiple_choice" or answer_style == "all":
            segments = self._split_into_segments(text)

            for segment in segments:
                sentences = self._split_text(segment)
                prepped_inputs, prepped_answers = self._prepare_qg_inputs_MC(sentences)
                inputs.extend(prepped_inputs)
                answers.extend(prepped_answers)

        return inputs, answers

    def _encode_qg_input(self, qg_input: str) -> torch.tensor:
        return self.qg_tokenizer(
            qg_input,
            padding='max_length',
            max_length=self.SEQ_LENGTH,
            truncation=True,
            return_tensors='pt'
        ).to(self.device)

    @torch.no_grad()
    def _generate_question(self, qg_input: str) -> str:
        encoded_input = self._encode_qg_input(qg_input)
        output = self.qg_model.generate(input_ids=encoded_input['input_ids'])
        question = self.qg_tokenizer.decode(output[0], skip_special_tokens=True)

        return question

    def generate_questions_from_inputs(self, qg_inputs: List) -> List[str]:
        generated_questions = []

        for qg_input in qg_inputs:
            question = self._generate_question(qg_input)
            generated_questions.append(question)

        return generated_questions

    def _get_ranked_qa_pairs(self, generated_questions: List[str], qg_answers: List[str], scores, num_questions: int=10) -> List[Mapping[str, str]]:
        if num_questions > len(scores):
            num_questions = len(scores)
            print(f"\nWas only able to generate {num_questions} questions.", "For more questions, please provide longer text.")

        qa_list = []

        for i in range(num_questions):
            index = scores[i]
            qa = {"question": generated_questions[index].split("?")[0] + "?", "answer": qg_answers[index]}
            qa_list.append(qa)

        return qa_list

    def _get_all_qa_pairs(self, generated_questions: List[str], qg_answers: List[str]):
        qa_list = []

        for question, answer in zip(generated_questions, qg_answers):
            qa = {"question": question.split("?")[0] + "?", "answer": answer}
            qa_list.append(qa)

        return qa_list

    def generate(self, article, use_evaluator, num_questions, answer_style):
        print("Generating questions...\n")

        qg_inputs, qg_answers = self.generate_qg_inputs(article, answer_style)
        generated_questions = self.generate_questions_from_inputs(qg_inputs)

        message = "{} questions doesn't match {} answers".format(len(generated_questions), len(qg_answers))
        assert len(generated_questions) == len(qg_answers), message

        if use_evaluator:
            print("Evaluating QA pairs...\n")

            encoded_qa_pairs = self.qa_evaluator.encode_qa_pairs(generated_questions, qg_answers)
            scores = self.qa_evaluator.get_scores(encoded_qa_pairs)

            if num_questions:
                qa_list = self._get_ranked_qa_pairs(generated_questions, qg_answers, scores, num_questions)
            else:
                qa_list = self._get_ranked_qa_pairs(generated_questions, qg_answers, scores)
        else:
            print("Skipping evaluation...\n")
            qa_list = self._get_all_qa_pairs(generated_questions, qg_answers)

        return qa_list