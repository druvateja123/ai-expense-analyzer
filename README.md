AI Expense Analyzer

A Streamlit app that categorizes expenses with an LLM and answers questions about spending. Upload a CSV of transactions, and Gemini sorts each one into a category. The app shows a chart and answers questions in plain English.

Features

Upload a CSV with `date`, `description` and `amount`
Gemini Flash categorizes every transaction using structured JSON output
Validation: the app checks that the AI returned one category per transaction, and unknown categories become "Other"
Automatic retry when the API is busy
Bar chart of spending by category
Ask questions like "Which month did I spend the most?"
Pandas computes all totals, and the AI only explains them. This avoids made-up numbers on financial data.

Screenshots
[Results](screenshots/results.png)
[Results 2](screenshots/results2.png)
[Results 3](screenshots/result3.png)

Tech stack
Python, Streamlit, Pandas, Google Gemini API (`google-genai`), python-dotenv

How it works

1\. The CSV is loaded with Pandas.

2\. Transaction descriptions are sent to Gemini, which returns a JSON list of categories.

3\. The output is validated, then shown in a table and chart.

4\. For questions, Pandas computes totals by category and month, and Gemini answers using only those computed numbers.

Setup
bash
git clone <your-repo-url>
cd ai-expense-analyzer
python -m pip install -r requirements.txt

```

Create a `.env` file with your key (get one at aistudio.google.com):

```

GEMINI\_API\_KEY=

```
Run

```bash

python -m streamlit run app.py

```
Then upload `sample\_expenses.csv`.

Limitations

Categories are model-generated and may be wrong for unclear descriptions
Large files are sent in one request, so very big CSVs need batching
No database, and data is not saved between sessions

Future work

FastAPI backend and SQL storage
Batching for large files and an accuracy evaluation against hand-labeled data
Anomaly detection and monthly budget alerts
Bank statement PDF upload



Author

Panta Druva Teja, M.Sc. Data Science and Analytics

