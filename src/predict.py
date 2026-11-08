"""Classify new tweets with the Logistic Regression model from notebook 03.

The text pipeline mirrors notebook 02 so the model sees input in the
same shape it was trained on.
"""

from __future__ import annotations

import pickle
import re
from functools import lru_cache

from src.data import ROOT

MODELS_DIR = ROOT / "models"
NEGATION_WORDS = {"not", "no", "nor", "neither", "never", "n't", "nothing", "nobody"}


def clean_text(text: str) -> str:
    """Same cleaning steps as notebook 02 (`clean_text`)."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#", "", text)
    text = text.replace("&amp;", "and").replace("&lt;", "")
    text = text.replace("&gt;", "").replace("&quot;", "")
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
    """Stopword removal from notebook 02. After `clean_text` the text holds
    only letters and single spaces, so splitting on spaces gives the same
    tokens as NLTK's `word_tokenize`."""
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
