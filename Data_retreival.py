import os
import json
import re
import requests
import PyPDF2
import pdfplumber
import pandas as pd
import yfinance as yf
import google.generativeai as genai
from config import GEMINI_API_KEY  # Securely load API Key


genai.configure(api_key=GEMINI_API_KEY)  # Configure Gemini API

model = genai.GenerativeModel('gemini-pro')

### ---------------- PDF TEXT EXTRACTION ---------------- ###
def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text.strip()

### ---------------- COMPANY NAME EXTRACTION ---------------- ###
def extract_company_name_llm(text):
    """Extracts the company name from a financial report using Gemini API."""
    prompt = f"Extract the company name from the following financial report:\n{text[:2000]}"  
    response = model.generate_content(prompt)
    return response.text.strip()

### ---------------- KEY METRICS EXTRACTION ---------------- ###
def extract_key_metrics_llm(text):
    """Extracts key financial metrics using Gemini API."""
    prompt = f"""
    Extract key financial metrics from the following financial report. If a metric is not explicitly mentioned, return null.

    Required Metrics:
    - Revenue (Yearly and Quarterly)
    - Expenses (Yearly and Quarterly)
    - Net Profit (Yearly and Quarterly)
    - EBITDA (Yearly and Quarterly)
    - Margins (Yearly and Quarterly)
    - Assets (Total)
    - Liabilities (Total)
    - Equity (Total)
    - Investing Cash Flow (Total)
    - Operating Cash Flow (Total)
    - Financing Cash Flow (Total)

    Return the data **strictly** in **valid JSON format**, without any additional text or markdown formatting.

    Text:
    {text[:2000]}
    """
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Remove markdown JSON formatting if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        # Parse JSON output
        key_metrics = json.loads(response_text)
        return key_metrics
    except (json.JSONDecodeError, AttributeError):
        print("Error: Failed to parse JSON output from Gemini API.")
        return None

### ---------------- JSON TO DATAFRAME CONVERSION ---------------- ###
def json_to_dataframe(key_metrics):
    """Converts extracted financial metrics JSON into a structured Pandas DataFrame."""
    data = []
    
    for metric, values in key_metrics.items():
        if isinstance(values, dict):  # Check if it has Yearly/Quarterly subkeys
            for period_type, period_data in values.items():
                if isinstance(period_data, dict):  # Yearly/Quarterly data
                    for year, value in period_data.items():
                        data.append({"Metric": metric, "Type": period_type, "Year": year, "Value": value})
                else:
                    data.append({"Metric": metric, "Type": period_type, "Year": None, "Value": period_data})
        else:
            data.append({"Metric": metric, "Type": "Total", "Year": None, "Value": values})

    df = pd.DataFrame(data)
    df["Value"] = pd.to_numeric(df["Value"].astype(str).str.replace(",", ""), errors='coerce')

    return df

### ---------------- YAHOO FINANCE TICKER FETCHING ---------------- ###
def get_ticker_from_search(company_name):
    """Fetches the stock ticker symbol for a company using Yahoo Finance."""
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        res = requests.get(url, params=params, headers=headers)
        data = res.json()
        if data['quotes']:
            return data['quotes'][0]['symbol']
    except Exception as e:
        print(f"Error fetching ticker for {company_name}: {e}")
    return None

### ---------------- FINANCIAL METRICS FETCHING FROM YAHOO FINANCE ---------------- ###
def fetch_financial_metrics(ticker):
    """Extracts key financial metrics from Yahoo Finance for a given ticker."""
    try:
        company = yf.Ticker(ticker)
        
        # Extract Financial Statements
        financials = company.financials
        balance_sheet = company.balance_sheet
        cash_flow = company.cashflow
        
        return {
            # Income Statement Metrics
            "Revenue": financials.loc["Total Revenue"].iloc[0] if "Total Revenue" in financials.index else None,
            "Expenses": financials.loc["Total Operating Expenses"].iloc[0] if "Total Operating Expenses" in financials.index else None,
            "Net Profit": financials.loc["Net Income"].iloc[0] if "Net Income" in financials.index else None,
            "EBITDA": financials.loc["EBITDA"].iloc[0] if "EBITDA" in financials.index else None,
            "Margins": financials.loc["Gross Profit"].iloc[0] / financials.loc["Total Revenue"].iloc[0] if "Gross Profit" in financials.index and "Total Revenue" in financials.index else None,

            # Balance Sheet Metrics
            "Total Assets": balance_sheet.loc["Total Assets"].iloc[0] if "Total Assets" in balance_sheet.index else None,
            "Total Liabilities": balance_sheet.loc["Total Liabilities Net Minority Interest"].iloc[0] if "Total Liabilities Net Minority Interest" in balance_sheet.index else None,
            "Equity": balance_sheet.loc["Ordinary Shares Number"].iloc[0] if "Ordinary Shares Number" in balance_sheet.index else None,

            # Cash Flow Metrics
            "Operating Cash Flow": cash_flow.loc["Total Cash From Operating Activities"].iloc[0] if "Total Cash From Operating Activities" in cash_flow.index else None,
            "Investing Cash Flow": cash_flow.loc["Total Cashflows From Investing Activities"].iloc[0] if "Total Cashflows From Investing Activities" in cash_flow.index else None,
            "Financing Cash Flow": cash_flow.loc["Total Cash From Financing Activities"].iloc[0] if "Total Cash From Financing Activities" in cash_flow.index else None,
        }
    except Exception as e:
        print(f"Error fetching financial metrics for {ticker}: {e}")
        return None


### ---------------- MAIN DATA FETCH FUNCTION ---------------- ###
def fetch_data(company_name, competitors):
    """Fetches financial data for the main company and its competitors."""
    main_ticker = get_ticker_from_search(company_name)
    main_financials = fetch_financial_metrics(main_ticker)

    competitors_data = {}
    for competitor in competitors:
        competitor_ticker = get_ticker_from_search(competitor)
        competitor_financials = fetch_financial_metrics(competitor_ticker)
        competitors_data[competitor] = {
            "ticker": competitor_ticker,
            "financial_metrics": competitor_financials
        }

    return {
        "main_company": {
            "name": company_name,
            "ticker": main_ticker,
            "financial_metrics": main_financials
        },
        "competitors": competitors_data
    }

def main():
    # Step 1: Ask for financial report
    pdf_path = input("Enter the path to the financial report PDF: ")
    
    # Step 2: Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Step 3: Extract company name and print it
    company_name = extract_company_name_llm(text)
    print("\nExtracted Company Name:", company_name)

    # Step 4: Extract key metrics from the financial report and print
    key_metrics = extract_key_metrics_llm(text)
    if key_metrics:
        df_metrics = json_to_dataframe(key_metrics)
        print("\nExtracted Key Financial Metrics:\n", df_metrics)

    # Step 5: Ask user for competitor names
    competitors = input("\nEnter competitor company names (comma-separated): ").split(",")

    # Step 6: Fetch ticker symbols and key metrics for competitors
    competitor_data = {}
    for competitor in competitors:
        competitor = competitor.strip()
        ticker = get_ticker_from_search(competitor)
        if ticker:
            competitor_metrics = fetch_financial_metrics(ticker)
            competitor_data[competitor] = competitor_metrics

    # Step 7: Convert competitor data to DataFrame
    competitor_df = pd.DataFrame.from_dict(competitor_data, orient="index")

    # Step 8: Print competitor data
    print("\nCompetitor Financial Metrics:\n", competitor_df)

    # Step 9: Ask for earnings call transcript
    transcript_path = input("\nEnter the path to the earnings call transcript PDF: ")

    # Step 10: Extract text from transcript PDF
    transcript_text = extract_text_from_pdf(transcript_path)
    print("\nExtracted Earnings Call Transcript (First 500 characters):\n", transcript_text[:500])

if __name__ == "__main__":
    main()