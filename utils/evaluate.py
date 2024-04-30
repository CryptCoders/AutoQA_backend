import nltk, string, math
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt')

lemmatizer = nltk.stem.WordNetLemmatizer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [lemmatizer.lemmatize(item) for item in tokens]

def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    try:
        tfidf = vectorizer.fit_transform([text1, text2])
        return math.ceil((tfidf * tfidf.T).A[0, 1] * 10)
    except Exception as e:
        print(e)
        return 0