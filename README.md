# Sentiment Analysis Dashboard

End-to-end sentiment analysis project with interactive Streamlit dashboard. Analyzes social media / review text data, classifies sentiment (positive / negative / neutral), and visualizes insights.

## 🎯 Project Goals

- Build a reproducible NLP pipeline for sentiment classification
- Deploy an interactive dashboard for non-technical users to explore results
- Demonstrate end-to-end ML workflow: data → model → deployment

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **NLP:** NLTK / VADER / HuggingFace Transformers
- **Data:** pandas, numpy
- **Viz:** Plotly, Matplotlib, WordCloud
- **Dashboard:** Streamlit
- **Deployment:** Streamlit Community Cloud

## 📁 Project Structure

```
sentiment-analysis-dashboard/
├── data/
│   ├── raw/              # Dataset asli (jangan di-commit kalau gede)
│   └── processed/        # Data yang udah dibersihin
├── notebooks/            # Jupyter notebooks buat eksplorasi
├── src/                  # Reusable Python modules
│   ├── preprocessing.py
│   ├── sentiment.py
│   └── utils.py
├── app/                  # Streamlit dashboard
│   └── streamlit_app.py
├── models/               # Saved models (kalau ada)
├── tests/                # Unit tests
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Clone repo
```bash
git clone https://github.com/USERNAME/sentiment-analysis-dashboard.git
cd sentiment-analysis-dashboard
```

### 2. Setup virtual environment
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run dashboard
```bash
streamlit run app/streamlit_app.py
```

## 📊 Dataset

[TBD — isi nanti pas udah pilih dataset]

## 📈 Results

[TBD — screenshot dashboard & metrics setelah selesai]

## 👤 Author

[Nama lo] — [link LinkedIn / portfolio]

## 📄 License

MIT
