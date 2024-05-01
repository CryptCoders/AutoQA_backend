import spacy
from nltk.corpus import wordnet

nlp = spacy.load("en_core_web_sm")

def calculate_jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def text_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)

    tokens1 = [token.lemma_ for token in doc1]
    tokens2 = [token.lemma_ for token in doc2]

    if tokens1 == tokens2:
        return 10

    synonyms1 = set()
    synonyms2 = set()

    for token in doc1:
        for syn in wordnet.synsets(token.text):
            for lemma in syn.lemmas():
                synonyms1.add(lemma.name().lower())

    for token in doc2:
        for syn in wordnet.synsets(token.text):
            for lemma in syn.lemmas():
                synonyms2.add(lemma.name().lower())

    synonym_similarity = calculate_jaccard_similarity(synonyms1, synonyms2)

    overall_similarity = synonym_similarity * 10
    return round(overall_similarity, 1)