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
def extract_company_name_llm(text,api_key=GEMINI_API_KEY):
    """Extracts the company name from a financial report using Gemini API."""
    prompt = f"Extract the company name from the following financial report:\n{text[:2000]}"  
    response = model.generate_content(prompt)
    return response.text.strip()

### ---------------- KEY METRICS EXTRACTION ---------------- ###

def extract_key_metrics_llm(text):
    """Use Gemini API to extract financial metrics for all years from the report."""
    prompt = f"""
    Extract financial data from this report text and return only JSON.
    
    {text}
    
    Return JSON in this exact format (no extra text):
    {{
      "financials": [
        {{
          "year": 2023,
          "Revenue": numbers,
          "EBITDA": numbers,
          "Net Profit": numbers,
          "Total Assets": numbers,
          "Total Liabilities": numbers,
          "Equity": numbers,
          "Operating Cash Flow": numbers,
          "Investing Cash Flow": numbers,
          "Financing Cash Flow": numbers
        }},
        {{
          "year": 2022,
          "Revenue": numbers,
          "EBITDA": numbers,
          "Net Profit": numbers,
          "Total Assets": numbers,
          "Total Liabilities": numbers,
          "Equity": numbers,
          "Operating Cash Flow": numbers,
          "Investing Cash Flow": numbers,
          "Financing Cash Flow": numbers
        }},
         {{
          "year": 2021,
          "Revenue": numbers,
          "EBITDA": numbers,
          "Net Profit": numbers,
          "Total Assets": numbers,
          "Total Liabilities": numbers,
          "Equity": numbers,
          "Operating Cash Flow": numbers,
          "Investing Cash Flow": numbers,
          "Financing Cash Flow": numbers
        }}
      ]
    }}
    """

    try:
        # Call Gemini API
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        # Debugging: Print full response
        print("Gemini API Raw Response:", response)

        # Extract the JSON content from the response
        response_text = response.text.strip()

        # Clean response to extract only JSON part
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        else:
            print("No valid JSON detected in response.")
            return None

        # Parse JSON response
        extracted_data = json.loads(response_text)
        financials = extracted_data.get("financials", [])

        # Convert to DataFrame
        df_pdf = pd.DataFrame(financials)

        # Melt into long format
        df_melted = df_pdf.melt(id_vars=["year"], var_name="Metric", value_name="Value")
        df_melted.rename(columns={"year": "Year"}, inplace=True)

        return df_melted

    except json.JSONDecodeError as e:
        print("JSON Parsing Error:", e)
        print("Gemini Response Text:", response_text)
        return None
    except Exception as e:
        print("Unexpected Error:", e)
        return None

# ### ---------------- JSON TO DATAFRAME CONVERSION ---------------- ###
# def json_to_dataframe(key_metrics):
#     """Converts extracted financial metrics JSON into a structured Pandas DataFrame."""
#     data = []
    
#     for metric, values in key_metrics.items():
#         if isinstance(values, dict):  # Check if it has Yearly/Quarterly subkeys
#             for period_type, period_data in values.items():
#                 if isinstance(period_data, dict):  # Yearly/Quarterly data
#                     for year, value in period_data.items():
#                         data.append({"Metric": metric, "Type": period_type, "Year": year, "Value": value})
#                 else:
#                     data.append({"Metric": metric, "Type": period_type, "Year": None, "Value": period_data})
#         else:
#             data.append({"Metric": metric, "Type": "Total", "Year": None, "Value": values})

#     df = pd.DataFrame(data)
#     df["Value"] = pd.to_numeric(df["Value"].astype(str).str.replace(",", ""), errors='coerce')

#     return df

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
def fetch_financial_metrics(ticker_symbol, years=3):
    stock = yf.Ticker(ticker_symbol)

    # Get available data periods
    income_stmt = stock.financials
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow

    # Extract the latest available years
    available_years = sorted(list(income_stmt.columns.year), reverse=True)

    # Get only the past 'years' financial data
    selected_years = available_years[:years]

    financial_data = []

    for year in selected_years:
        try:
            year_data = {
                "Year": year,
                "Revenue": income_stmt.loc["Total Revenue", str(year)].iloc[0] if "Total Revenue" in income_stmt.index else None,
                "EBITDA": income_stmt.loc["EBITDA", str(year)].iloc[0] if "EBITDA" in income_stmt.index else None,
                "Net Profit": income_stmt.loc["Net Income", str(year)].iloc[0] if "Net Income" in income_stmt.index else None,
                "Margins": (income_stmt.loc["EBITDA", str(year)].iloc[0] / income_stmt.loc["Total Revenue", str(year)].iloc[0])
                           if "EBITDA" in income_stmt.index and "Total Revenue" in income_stmt.index else None,
                "Total Assets": balance_sheet.loc["Total Assets", str(year)].iloc[0] if "Total Assets" in balance_sheet.index else None,
                "Total Liabilities": balance_sheet.loc["Total Liabilities Net Minority Interest", str(year)].iloc[0]
                                     if "Total Liabilities Net Minority Interest" in balance_sheet.index else None,
                "Equity": balance_sheet.loc["Stockholders Equity", str(year)].iloc[0] if "Stockholders Equity" in balance_sheet.index else None,
                "Operating Cash Flow": cash_flow.loc["Operating Cash Flow", str(year)].iloc[0] if "Operating Cash Flow" in cash_flow.index else None,
                "Investing Cash Flow": cash_flow.loc["Investing Cash Flow", str(year)].iloc[0] if "Investing Cash Flow" in cash_flow.index else None,
                "Financing Cash Flow": cash_flow.loc["Financing Cash Flow", str(year)].iloc[0] if "Financing Cash Flow" in cash_flow.index else None,
            }
            financial_data.append(year_data)
        except KeyError:
            continue  # Skip if any key is missing

    # Convert to DataFrame
    df = pd.DataFrame(financial_data)

    # Convert to long-format table (Year | Metric | Value)
    df_melted = df.melt(id_vars=["Year"], var_name="Metric", value_name="Value")

    return df_melted


def main():
    # Step 1: Ask for financial report PDF path
    pdf_path = input("Enter the path to the financial report PDF: ")

    # Step 2: Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Step 3: Extract company name from the report
    company_name = extract_company_name_llm(text, api_key=GEMINI_API_KEY)
    print("\nExtracted Company Name:", company_name)

    # Step 4: Extract key metrics from the financial report
    df_metrics = extract_key_metrics_llm(text)
    if df_metrics is None:
        print("Error extracting key financial metrics from the report.")
        return

    print("\nExtracted Key Financial Metrics:\n", df_metrics)

     # Step 5: Ask user for competitor names
    competitors = input("\nEnter competitor company names (comma-separated): ").split(",")
    competitors = [comp.strip() for comp in competitors]  # Clean up spaces

    # Step 6: Get tickers for each competitor
    competitor_data = []
    for competitor in competitors:
        ticker = get_ticker_from_search(competitor)
        if ticker:
            data = fetch_financial_metrics(ticker)
            if data is not None:
                data["Company"] = competitor  # Add company name for identification
                competitor_data.append(data)
            else:
                print(f"Warning: No financial data found for {competitor}.")
        else:
            print(f"Warning: Could not find ticker for {competitor}.")

    # Step 7: Combine competitor data
    if competitor_data:
        competitors_df = pd.concat(competitor_data, ignore_index=True)
        print("\nCompetitor Financial Data:\n", competitors_df)
    else:
        print("\nError: Could not generate competitor comparison table.")

    # Step 7: Ask for earnings call transcript (Optional)
    transcript_path = input("\nEnter the path to the earnings call transcript PDF (or press Enter to skip): ").strip()

    if transcript_path:
        transcript_text = extract_text_from_pdf(transcript_path)
        print("\nExtracted Earnings Call Transcript (First 500 characters):\n", transcript_text[:500])

if __name__ == "__main__":
    main()

