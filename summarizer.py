
import json
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import GEMINI_API_KEY
from Data_retrieval import get_ticker_from_search,fetch_financial_metrics,extract_text_from_pdf,extract_company_name_llm,extract_key_metrics_llm  # Import your data retrieval module

genai.configure(api_key=GEMINI_API_KEY)  # Configure Gemini API
model = genai.GenerativeModel('gemini-pro')


### ---------------- SUMMARIZATION FUNCTIONS ---------------- ###
def summarize_text(text, context="financial report"):
    """
    Uses Gemini API to summarize a given text.
    :param text: The text to summarize (from financial reports or earnings call transcripts)
    :param context: The type of content being summarized.
    :return: Summarized text
    """
    prompt = f"""
    Summarize the following {context} in a concise and structured format.
    Highlight the key insights, trends, and important points.
    
    Text:
    {text[:3000]}  # Limit input to 3000 characters to avoid token issues
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error summarizing {context}: {e}")
        return None
    
def summarize_financial_metrics(metrics_df):
    """
    Generates a **short paragraph** summary of the financial metrics.
    :param metrics_df: Pandas DataFrame containing financial metrics
    :return: Summary text
    """
    if metrics_df.empty:
        return "No financial metrics available."

    prompt = f"""
    Given the following key financial metrics, provide a very concise summary (within 3-5 sentences).
    Highlight revenue trends, profitability, cash flow performance  and other significant insights briefly.
    
    Financial Data:
    {metrics_df.to_string(index=False)}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error summarizing financial metrics:", e)
        return None



def compare_metrics(main_company_name, competitors):
    """Fetches financial data for the main company and competitors and arranges it for easy comparison."""
    
    # Fetch main company ticker and financial data
    main_ticker = get_ticker_from_search(main_company_name)
    if not main_ticker:
        print(f"Error: Could not find ticker for {main_company_name}")
        return None

    main_df = fetch_financial_metrics(main_ticker)
    if main_df is None:
        print(f"Error: Could not fetch financial metrics for {main_company_name}")
        return None

    # Add company name column to main company dataframe
    main_df["Company"] = main_company_name

    # Fetch competitor financials
    competitor_data = []
    for competitor in competitors:
        competitor = competitor.strip()
        ticker = get_ticker_from_search(competitor)

        if ticker:
            competitor_df = fetch_financial_metrics(ticker)
            if competitor_df is not None:
                competitor_df["Company"] = competitor
                competitor_data.append(competitor_df)
            else:
                print(f"Warning: No financial data for {competitor}")

    # Combine all data
    all_data = [main_df] + competitor_data  # List of DataFrames
    final_df = pd.concat(all_data, axis=0).reset_index(drop=True)

    # Sort by Year and Metric (to align competitors with main company)
    final_df.sort_values(by=["Metric", "Year"], ascending=[True, False], inplace=True)

    return final_df

def summarize_comparison(main_company_metrics, competitor_metrics):
    """
    Compares the main company's financial metrics with competitors.
    :param main_company_metrics: Pandas DataFrame of main company metrics.
    :param competitor_metrics: Pandas DataFrame of competitor metrics.
    :return: Summary text
    """
    prompt = f"""
    Compare the financial performance of the main company with its competitor(s) based on the given metrics.
    Identify strengths, weaknesses, and competitive advantages.

    Main Company Metrics:
    {main_company_metrics.to_string(index=False)}

    Competitor Metrics:
    {competitor_metrics.to_string(index=False)}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error in competitor comparison:", e)
        return None

def plot_comparison(df_comparison):
    """Generates bar plots for key financial metrics."""
    df_comparison.set_index("Company", inplace=True)
    
    plt.figure(figsize=(14, 8))
    for metric in df_comparison.columns:
        plt.figure(figsize=(10, 6))
        sns.barplot(x=df_comparison.index, y=df_comparison[metric], palette="viridis")
        plt.title(f"Comparison of {metric}")
        plt.xticks(rotation=45)
        plt.ylabel(metric)
        plt.tight_layout()
        plt.show()


### ---------------- MAIN EXECUTION ---------------- ###
def main():
    pdf_path = input("Enter the path to the financial report PDF: ")
    report_text = extract_text_from_pdf(pdf_path)

    company_name = extract_company_name_llm(report_text)
    print("\nExtracted Company Name:", company_name)

    key_metrics_df = extract_key_metrics_llm(report_text)
    print("\nExtracted Key Financial Metrics:\n", key_metrics_df)

    report_summary = summarize_text(report_text, context="financial report")
    print("\nFinancial Report Summary:\n", report_summary)

    competitors = input("\nEnter competitor company names (comma-separated): ").split(",")
    competitors = [comp.strip() for comp in competitors]

    df_comparison = compare_metrics(company_name, competitors)

    if df_comparison is None or df_comparison.empty:
        print("Error: Unable to retrieve financial data for comparison.")
        return

    main_company_data = df_comparison[df_comparison["Company"] == company_name]
    competitor_data = df_comparison[df_comparison["Company"] != company_name]

    financial_summary = summarize_financial_metrics(main_company_data)
    print("\nFinancial Metrics Summary:\n", financial_summary)

    print("\nMain Company Financial Metrics:\n", main_company_data)
    print("\nCompetitor Financial Metrics:\n", competitor_data)

    comparison_summary = summarize_comparison(main_company_data, competitor_data)
    print("\nComparison Summary:\n", comparison_summary)

    plot_comparison(df_comparison)

    transcript_path = input("\nEnter the path to the earnings call transcript PDF (or press Enter to skip): ").strip()
    if transcript_path:
        transcript_text = extract_text_from_pdf(transcript_path)
        transcript_summary = summarize_text(transcript_text, context="earnings call transcript")
        print("\nEarnings Call Transcript Summary:\n", transcript_summary)
    else:
        print("\nNo transcript provided. Skipping transcript summarization.")

if __name__ == "__main__":
    main()


# def summarize_text(text, context="financial report"):
#     """
#     Uses Gemini API to summarize a given text.
#     :param text: The text to summarize (from financial reports or earnings call transcripts)
#     :param context: The type of content being summarized.
#     :return: Summarized text
#     """
#     prompt = f"""
#     Summarize the following {context} in a concise and structured format.
#     Highlight the key insights, trends, and important points.
    
#     Text:
#     {text[:3000]}  # Limit input to 3000 characters to avoid token issues
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         print(f"Error summarizing {context}: {e}")
#         return None

# def summarize_financial_metrics(metrics_df):
#     """
#     Generates a textual summary of the financial metrics DataFrame.
#     :param metrics_df: Pandas DataFrame containing financial metrics
#     :return: Summary text
#     """
#     if metrics_df.empty:
#         return "No financial metrics available."

#     prompt = f"""
#     Given the following key financial metrics, provide a concise summary highlighting revenue trends,
#     profitability, cash flow performance, and other significant insights.

#     Financial Data:
#     {metrics_df.to_string(index=False)}
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         print("Error summarizing financial metrics:", e)
#         return None