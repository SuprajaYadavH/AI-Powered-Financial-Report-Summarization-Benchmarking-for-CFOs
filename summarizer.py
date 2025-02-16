
import json
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import GEMINI_API_KEY
import Data_retrieval  # Import your data retrieval module

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
    Generates a textual summary of the financial metrics DataFrame.
    :param metrics_df: Pandas DataFrame containing financial metrics
    :return: Summary text
    """
    if metrics_df.empty:
        return "No financial metrics available."

    prompt = f"""
    Given the following key financial metrics, provide a concise summary highlighting revenue trends,
    profitability, cash flow performance, and other significant insights.

    Financial Data:
    {metrics_df.to_string(index=False)}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error summarizing financial metrics:", e)
        return None


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


### ---------------- BENCHMARKING FUNCTIONS ---------------- ###
def compare_metrics(main_company_data, competitors_data):
    """
    Arranges financial metrics of the main company and competitors into a single DataFrame for comparison.
    """
    metrics = ["Revenue", "Net Profit", "Margins", "Total Assets", "Total Liabilities", "Equity", "Operating Cash Flow"]
    
    # Concatenate data from the main company and competitors
    all_data = [main_company_data["financial_metrics"]]
    
    for competitor, details in competitors_data.items():
        all_data.append(details["financial_metrics"])
    
    # Create a single DataFrame
    df_comparison = pd.concat(all_data, ignore_index=True)
    
    return df_comparison


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
    """
    Main function to perform financial data extraction and summarization.
    """
    # Step 1: Extract financial report and earnings call transcript
    pdf_path = input("Enter the path to the financial report PDF: ")
    report_text = Data_retrieval.extract_text_from_pdf(pdf_path)

    # Step 2: Extract company name
    company_name = Data_retrieval.extract_company_name_llm(report_text)
    print("\nExtracted Company Name:", company_name)

    # Step 3: Extract financial metrics
    key_metrics_df = Data_retrieval.extract_key_metrics_llm(report_text)
    print("\nExtracted Key Financial Metrics:\n", key_metrics_df)

    # Step 4: Summarize financial report
    report_summary = summarize_text(report_text, context="financial report")
    print("\nFinancial Report Summary:\n", report_summary)

    # Step 5: Get competitor names and extract their metrics
    competitors = input("\nEnter competitor company names (comma-separated): ").split(",")
    competitors = [comp.strip() for comp in competitors]

    # Fetch data for the main company and competitors
    all_data = Data_retrieval.fetch_data(company_name, competitors)

    # Separate main company and competitor data
    main_company_data = all_data[all_data["Company"] == company_name]
    competitor_data = all_data[all_data["Company"] != company_name]

    print("\nMain Company Financial Metrics:\n", main_company_data)
    print("\nCompetitor Financial Metrics:\n", competitor_data)

    # Step 6: Summarize financial metrics
    financial_summary = summarize_financial_metrics(main_company_data)
    print("\nFinancial Metrics Summary:\n", financial_summary)

    # Step 7: Compare main company vs competitors
    df_comparison = pd.concat([main_company_data, competitor_data], ignore_index=True)
    print("\nFinancial Metrics Comparison:\n", df_comparison)

    comparison_summary = summarize_comparison(main_company_data, competitor_data)
    print("\nComparison Summary:\n", comparison_summary)

    # Step 8: Plot financial comparisons
    plot_comparison(df_comparison)

    # Step 9: Extract and summarize earnings call transcript
    transcript_path = input("\nEnter the path to the earnings call transcript PDF: ")
    transcript_text = Data_retrieval.extract_text_from_pdf(transcript_path)
    
    transcript_summary = summarize_text(transcript_text, context="earnings call transcript")
    print("\nEarnings Call Transcript Summary:\n", transcript_summary)


if __name__ == "__main__":
    main()

# import json
# import google.generativeai as genai
# from config import GEMINI_API_KEY 
# import Data_retrieval  # Import your data retrieval module

# genai.configure(api_key=GEMINI_API_KEY)  # Configure Gemini API

# model = genai.GenerativeModel('gemini-pro')


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


# def summarize_comparison(main_company_metrics, competitor_metrics):
#     """
#     Compares the main company's financial metrics with competitors.
#     :param main_company_metrics: Pandas DataFrame of main company metrics.
#     :param competitor_metrics: Pandas DataFrame of competitor metrics.
#     :return: Summary text
#     """
#     prompt = f"""
#     Compare the financial performance of the main company with its competitor(s) based on the given metrics.
#     Identify strengths, weaknesses, and competitive advantages.

#     Main Company Metrics:
#     {main_company_metrics.to_string(index=False)}

#     Competitor Metrics:
#     {competitor_metrics.to_string(index=False)}
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         print("Error in competitor comparison:", e)
#         return None


# def main():
#     """
#     Main function to perform financial data extraction and summarization.
#     """
#     # Step 1: Extract financial report and earnings call transcript
#     pdf_path = input("Enter the path to the financial report PDF: ")
#     report_text = Data_retrieval.extract_text_from_pdf(pdf_path)

#     # Step 2: Extract company name
#     company_name = Data_retrieval.extract_company_name_llm(report_text)
#     print("\nExtracted Company Name:", company_name)

#     # Step 3: Extract financial metrics
#     key_metrics = Data_retrieval.extract_key_metrics_llm(report_text)
#     key_metrics_df = Data_retrieval.json_to_dataframe(key_metrics)
#     print("\nExtracted Key Financial Metrics:\n", key_metrics_df)

#     # Step 4: Summarize financial report
#     report_summary = summarize_text(report_text, context="financial report")
#     print("\nFinancial Report Summary:\n", report_summary)

#     # Step 5: Get competitor names and extract their metrics
#     competitors = input("\nEnter competitor company names (comma-separated): ").split(",")
#     competitor_data = Data_retrieval.fetch_data(company_name, competitors)
    
#     competitor_metrics_df = Data_retrieval.json_to_dataframe(competitor_data["competitors"])
#     print("\nCompetitor Financial Metrics:\n", competitor_metrics_df)

#     # Step 6: Summarize financial metrics
#     financial_summary = summarize_financial_metrics(key_metrics_df)
#     print("\nFinancial Metrics Summary:\n", financial_summary)

#     # Step 7: Compare main company vs competitors
#     comparison_summary = summarize_comparison(key_metrics_df, competitor_metrics_df)
#     print("\nComparison Summary:\n", comparison_summary)

#     # Step 8: Extract and summarize earnings call transcript
#     transcript_path = input("\nEnter the path to the earnings call transcript PDF: ")
#     transcript_text = Data_retrieval.extract_text_from_pdf(transcript_path)
    
#     transcript_summary = summarize_text(transcript_text, context="earnings call transcript")
#     print("\nEarnings Call Transcript Summary:\n", transcript_summary)


# if __name__ == "__main__":
#     main()
