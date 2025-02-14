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

# Main function to extract data and process the company's financial statements
def main():
    # Input for the main company PDF
    pdf_path = input("Enter the path to your financial report PDF: ")
    filename = os.path.basename(pdf_path)
    company_name = extract_company_name_from_filename(filename)
    print(f"Extracted Company Name: {company_name}")
    
    # Get the ticker for the main company
    ticker = get_ticker_from_search(company_name)
    main_company_data = None
    if ticker:
        print(f"Fetched Ticker Symbol for {company_name}: {ticker}")
        main_company_data = fetch_financial_data(ticker)
        financial_statements = fetch_financial_statements(ticker)
        financial_metrics = fetch_financial_metrics(ticker)
        
        if main_company_data is not None:
            print(f"\nMain Company Data for {ticker}:")
            print(main_company_data.head())  # Stock price data
            
            print("\nMain Company Financial Statements:")
            print("Income Statement:", financial_statements["Income Statement"])
            print("Balance Sheet:", financial_statements["Balance Sheet"])
            print("Cash Flow:", financial_statements["Cash Flow"])
            
            print("\nMain Company Financial Metrics:")
            print(financial_metrics)
        else:
            print("Could not retrieve financial data for the main company.")
    else:
        print("Could not fetch ticker symbol for the main company.")
    
    # Ask user for competitors' names
    competitors = input("Enter the names of competitors (separated by commas): ").split(',')
    competitors = [competitor.strip() for competitor in competitors]  # Clean up input

    competitor_data_dict = {}  # To store competitor data

    for competitor in competitors:
        print(f"\nProcessing competitor: {competitor}")
        
        # Get ticker for competitor
        competitor_ticker = get_ticker_from_search(competitor)
        if competitor_ticker:
            print(f"Fetched Ticker Symbol for {competitor}: {competitor_ticker}")
            competitor_data = fetch_financial_data(competitor_ticker)
            competitor_financial_statements = fetch_financial_statements(competitor_ticker)
            competitor_financial_metrics = fetch_financial_metrics(competitor_ticker)
            
            if competitor_data is not None:
                competitor_data_dict[competitor_ticker] = competitor_data
                print(f"Financial Data for {competitor_ticker} retrieved successfully.")
                
                print(f"\nCompetitor Data for {competitor_ticker}:")
                print(competitor_data.head())  # Stock price data
                
                print("\nCompetitor Financial Statements:")
                print("Income Statement:", competitor_financial_statements["Income Statement"])
                print("Balance Sheet:", competitor_financial_statements["Balance Sheet"])
                print("Cash Flow:", competitor_financial_statements["Cash Flow"])
                
                print("\nCompetitor Financial Metrics:")
                print(competitor_financial_metrics)
            else:
                print(f"Could not retrieve financial data for {competitor}.")
        else:
            print(f"Could not fetch ticker symbol for {competitor}.")

    # Now you have the data stored in variables:
    # - main_company_data: Contains the main company's stock data, financial data, and metrics
    # - competitor_data_dict: A dictionary containing competitor tickers and their stock data, financial data, and metrics

if __name__ == "__main__":
    main()
