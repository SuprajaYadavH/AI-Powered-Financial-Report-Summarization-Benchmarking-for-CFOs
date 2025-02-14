# AI-Powered Financial Report Summarization & Benchmarking for CFOs

## Overview

The goal of this project is to develop an AI-powered financial summarization and benchmarking tool that extracts key insights from financial reports, generates concise summaries, performs sentiment analysis, and presents data in an interactive dashboard for CFOs to make informed decisions efficiently.

## Features
- **Financial Data Extraction**: Extracts key metrics from balance sheets, P&L statements, and cash flow reports.
- **AI-Powered Summarization**: Uses Transformer-based NLP models (T5, GPT-4) to summarize financial statements.
- **Competitor Benchmarking**: Compares financial KPIs across competitors using AI-driven models.
- **Sentiment Analysis**: Analyzes earnings reports using FinBERT to detect positive or negative sentiment.
- **Interactive Dashboard**: Built with Streamlit and D3.js for intuitive data visualization.
- **Export Functionality**: Generates board-ready reports in PDF and PowerPoint formats.

---
## Installation & Setup
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended: `venv` or `conda`)

### Clone the Repository
```sh
git clone https://github.com/SuprajaYadavH/AI-Powered-Financial-Report-Summarization-Benchmarking-for-CFOs.git
cd AI-Powered-Financial-Report-Summarization-Benchmarking-for-CFOs
```

### Create and Activate a Virtual Environment
```sh
python -m venv venv  # Create a virtual environment
source venv/bin/activate  # Activate on macOS/Linux
venv\Scripts\activate  # Activate on Windows
```

### Install Dependencies
Install required Python libraries using:
```sh
pip install -r requirements.txt
```

### Setup API Keys
Some modules require API keys for external services. Add your keys in an `.env` file in the root directory:
```
GEMINI_API_KEY=your_gemini_api_key

```

---
## Running the Application
### 1. Start the Streamlit Dashboard
```sh
streamlit run app.py
```
This will launch the interactive web application in your browser.

### 2. Run Individual Components (Optional)
You can test specific functionalities separately:
```sh
python summarizer.py  # Runs the financial summarization module
python sentiment_analyzer.py  # Runs the sentiment analysis module
python benchmarking.py  # Runs financial benchmarking
python Data_retreival.py  # Extracts key financial metrics
```

---
## File Structure
```
├── dataset/                    # Financial datasets
├── .gitignore                   # Git ignore file
├── Data_retreival.py            # Key financial metrics extraction
├── app.py                        # Streamlit dashboard main file
├── app2.py                       # Additional Streamlit module (if needed)
├── benchmarking.py               # Competitor benchmarking
├── sentiment_analyzer.py         # Sentiment analysis
├── summarizer.py                 # Financial summarization
├── requirements.txt              # Python dependencies
├── README.md                     # Documentation
```

---
## Future Enhancements
- **Multi-Period Trend Analysis**: Compare financials over multiple quarters.
- **Earnings Call Summarization**: Using speech-to-text AI.
- **Automated Insights Generation**: Highlight key risks and trends.

---
## Contributors
- **Supraja Yadav H** - [GitHub](https://github.com/SuprajaYadavH)

---
## License
This project is licensed under the MIT License.

