import re
import os
import PyPDF2
import yfinance as yf
import requests

def extract_company_name_from_filename(filename):
    return filename.split('_')[0]  # Extract the first word as company name

def get_ticker_from_search(company_name):
    yfinance_url = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=yfinance_url, params=params, headers={'User-Agent': user_agent})
    data = res.json()

    if data['quotes']:
        company_code = data['quotes'][0]['symbol']
        return company_code
    return None

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def fetch_financial_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="5y")
        if data.empty:
            print(f"No data found for {ticker}.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None
    
def fetch_financial_statements(ticker):
    company = yf.Ticker(ticker)
    
    financials = company.financials  # Income Statement
    balance_sheet = company.balance_sheet
    cash_flow = company.cashflow

    # Convert to dictionary format
    return {
        "Income Statement": financials.to_dict(),
        "Balance Sheet": balance_sheet.to_dict(),
        "Cash Flow": cash_flow.to_dict(),
    }

def fetch_financial_metrics(ticker):
    """Extracts key financial metrics from Yahoo Finance for a given ticker."""
    company = yf.Ticker(ticker)

    # Income Statement
    financials = company.financials
    revenue = financials.loc["Total Revenue"].iloc[0] if "Total Revenue" in financials.index else None
    net_income = financials.loc["Net Income"].iloc[0] if "Net Income" in financials.index else None
    ebitda = financials.loc["EBITDA"].iloc[0] if "EBITDA" in financials.index else None

    # Balance Sheet
    balance_sheet = company.balance_sheet
    total_assets = balance_sheet.loc["Total Assets"].iloc[0] if "Total Assets" in balance_sheet.index else None

    # Cash Flow Statement (corrected names)
    cash_flow = company.cashflow
    operating_cash_flow = cash_flow.loc["Operating Cash Flow"].iloc[0] if "Operating Cash Flow" in cash_flow.index else None
    investing_cash_flow = cash_flow.loc["Investing Cash Flow"].iloc[0] if "Investing Cash Flow" in cash_flow.index else None
    financing_cash_flow = cash_flow.loc["Financing Cash Flow"].iloc[0] if "Financing Cash Flow" in cash_flow.index else None

    return {
        "Revenue": revenue,
        "Net Income": net_income,
        "EBITDA": ebitda,
        "Total Assets": total_assets,
        "Operating Cash Flow": operating_cash_flow,
        "Investing Cash Flow": investing_cash_flow,
        "Financing Cash Flow": financing_cash_flow
    }

def fetch_data(company_name, competitors):
    """Fetch the main company and competitors' data."""
    ticker = get_ticker_from_search(company_name)
    main_company_data = fetch_financial_data(ticker)
    financial_statements = fetch_financial_statements(ticker)
    financial_metrics = fetch_financial_metrics(ticker)
    
    competitor_data_dict = {}
    for competitor in competitors:
        competitor_ticker = get_ticker_from_search(competitor)
        competitor_data = fetch_financial_data(competitor_ticker)
        competitor_financial_statements = fetch_financial_statements(competitor_ticker)
        competitor_financial_metrics = fetch_financial_metrics(competitor_ticker)
        
        competitor_data_dict[competitor_ticker] = {
            "stock_data": competitor_data,
            "financial_statements": competitor_financial_statements,
            "financial_metrics": competitor_financial_metrics
        }
    
    return {
        "main_company": {
            "ticker": ticker,
            "stock_data": main_company_data,
            "financial_statements": financial_statements,
            "financial_metrics": financial_metrics
        },
        "competitors": competitor_data_dict
    }