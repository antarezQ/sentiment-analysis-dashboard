# Sentiment Analysis Dashboard

**🔗 Live dashboard: [airline-sentiment-antarez.streamlit.app](https://airline-sentiment-antarez.streamlit.app)**

Analysis of 14,640 tweets about six US airlines to find out **which airlines customers complain about most, why they complain, and what airlines should fix first**.

## 🎯 Business Problem

Twitter is where airline customers complain in public. A Customer Experience / Social Care team has limited people, so it needs to know where to focus. This project answers four questions:

1. How negative is public conversation about airlines?
2. Which airlines have the worst and best reputation on Twitter?
3. What drives customer complaints: operations (delays, cancellations) or customer service?
4. What should the Customer Experience team prioritize?

## 📌 Key Insights

| # | Insight |
|---|---|
| 1 | **62.7%** of tweets are negative and only 16.1% are positive. Customers use Twitter mainly to complain. |
| 2 | **US Airways** has the worst reputation (**77.7%** negative), followed by American (71.0%) and United (68.9%). **Virgin America** has the best (35.9% negative). |
| 3 | United, US Airways and American account for ~65% of tweet volume but **~75% of all negative tweets**. |
| 4 | **Customer service** is the #1 complaint driver (**31.7%** of negative tweets), bigger than late and cancelled flights combined (27.4%). |

## 💡 Recommendations

1. **Fix customer service before punctuality.** It is the biggest complaint driver and the one airlines control most directly (staff training, response time, empowering agents to resolve issues).
2. **Focus social care resources on United, US Airways and American**, which together generate ~75% of negative tweets.
3. **Notify passengers proactively about delays and cancellations**, with automatic rebooking options, so operational problems do not escalate into service complaints.
4. **Benchmark against Virgin America**, whose share of positive tweets (30.2%) is over 3× that of US Airways (9.2%).
5. **Monitor sentiment automatically.** The classification model in this project flags negative tweets so the social care team does not have to read every tweet manually.

> **Limitations:** the data covers about one week in February 2015, Twitter users skew toward customers who had a problem, and American Airlines tweets were only collected from 22 Feb. 99.8% of tweets labeled "Delta" in the source are addressed to @JetBlue, so the dashboard relabels them as JetBlue. Full details are in [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb).

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
git clone https://github.com/antarezQ/sentiment-analysis-dashboard.git
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

### 4. Build the dashboard data and run the dashboard
Put `Tweets.csv` in `data/raw/` first (see Dataset below).
```bash
python scripts/build_dashboard_data.py
streamlit run app/streamlit_app.py
```

To rerun the notebooks and tests, install `requirements-dev.txt` instead and run `pytest`.

## 📊 Dataset

[Twitter US Airline Sentiment](https://www.kaggle.com/datasets/crowdflower/twitter-airline-sentiment) (Kaggle / CrowdFlower): 14,640 tweets from February 2015, each labeled positive, neutral or negative by human annotators, with a complaint reason for negative tweets. Download `Tweets.csv` and place it in `data/raw/` (the dataset is not committed to this repo).

## 📈 Results

[TBD — screenshot dashboard & metrics setelah selesai]

## 👤 Author

[Nama lo] — [link LinkedIn / portfolio]

## 📄 License

MIT
