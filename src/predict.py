"""Text cleaning and sentiment prediction with the Logistic Regression model.

Notebook 03 imports `clean_text` and `to_tokens` from here to prepare the
training data, so the dashboard cleans new tweets exactly like the model
was trained.
"""

from __future__ import annotations

import pickle
import re
from functools import lru_cache

from src.data import ROOT

MODELS_DIR = ROOT / "models"
NEGATION_WORDS = {"not", "no", "nor", "neither", "never", "nothing", "nobody"}


def clean_text(text: str) -> str:
    """Clean a tweet for the models (used by notebook 03 and the dashboard).

    Contractions are expanded first ("didn't" -> "did not"). Otherwise the
    apostrophe is stripped, "didn" ends up as a separate token, and NLTK's
    stopword list removes it, so the negation would be lost.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower().replace("’", "'")
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#", "", text)
    text = text.replace("&amp;", "&").replace("&lt;", "").replace("&gt;", "").replace("&quot;", "")
    text = text.replace("&", " and ")
    text = re.sub(r"\bcan't\b", "can not", text)
    text = re.sub(r"\bwon't\b", "will not", text)
    text = re.sub(r"n't\b", " not", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=1)
def _stop_words() -> frozenset[str]:
    import nltk

    try:
        from nltk.corpus import stopwords

        words = stopwords.words("english")
    except LookupError:
        nltk.download("stopwords", quiet=True)
        from nltk.corpus import stopwords

        words = stopwords.words("english")
    return frozenset(set(words) - NEGATION_WORDS)


def to_tokens(text: str) -> str:
    """Clean the text and drop stopwords (negations are kept). This is the
    input of the TF-IDF models. After `clean_text` the text holds only letters
    and single spaces, so splitting on spaces is enough to tokenize."""
    stop = _stop_words()
    return " ".join(t for t in clean_text(text).split() if t not in stop and len(t) > 1)


@lru_cache(maxsize=1)
def _load_model():
    with open(MODELS_DIR / "tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open(MODELS_DIR / "logistic_regression.pkl", "rb") as f:
        model = pickle.load(f)
    return vectorizer, model


def predict(text: str) -> tuple[str, dict[str, float]]:
    """Return the predicted sentiment and the probability of each class."""
    vectorizer, model = _load_model()
    features = vectorizer.transform([to_tokens(text)])
    probs = model.predict_proba(features)[0]
    scores = {label: float(p) for label, p in zip(model.classes_, probs)}
    return max(scores, key=scores.get), scores
