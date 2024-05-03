import math, spacy
import numpy as np
from fuzzywuzzy import fuzz

nlp = spacy.load("en_core_web_lg")

def fuzzratio(text1, text2):
    return int(fuzz.ratio(text1, text2) / 10)

def spacy_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)

    return min(10, math.ceil(doc1.similarity(doc2) * 10))

def evaluate(text1, text2):
    score = np.mean(np.array([spacy_similarity(text1, text2), fuzzratio(text1, text2)]))

    return min(10, math.ceil(score))