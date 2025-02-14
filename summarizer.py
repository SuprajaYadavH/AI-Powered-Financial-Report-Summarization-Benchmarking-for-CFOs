import json
import google.generativeai as genai
from config import GEMINI_API_KEY 
import Data_retreival  # Import your data retrieval module

genai.configure(api_key=GEMINI_API_KEY)  # Configure Gemini API

model = genai.GenerativeModel('gemini-pro')


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


def main():
    """
    Main function to perform financial data extraction and summarization.
    """
    # Step 1: Extract financial report and earnings call transcript
    pdf_path = input("Enter the path to the financial report PDF: ")
    report_text = Data_retreival.extract_text_from_pdf(pdf_path)

    # Step 2: Extract company name
    company_name = Data_retreival.extract_company_name_llm(report_text)
    print("\nExtracted Company Name:", company_name)

    # Step 3: Extract financial metrics
    key_metrics = Data_retreival.extract_key_metrics_llm(report_text)
    key_metrics_df = Data_retreival.json_to_dataframe(key_metrics)
    print("\nExtracted Key Financial Metrics:\n", key_metrics_df)

    # Step 4: Summarize financial report
    report_summary = summarize_text(report_text, context="financial report")
    print("\nFinancial Report Summary:\n", report_summary)

    # Step 5: Get competitor names and extract their metrics
    competitors = input("\nEnter competitor company names (comma-separated): ").split(",")
    competitor_data = Data_retreival.fetch_data(company_name, competitors)
    
    competitor_metrics_df = Data_retreival.json_to_dataframe(competitor_data["competitors"])
    print("\nCompetitor Financial Metrics:\n", competitor_metrics_df)

    # Step 6: Summarize financial metrics
    financial_summary = summarize_financial_metrics(key_metrics_df)
    print("\nFinancial Metrics Summary:\n", financial_summary)

    # Step 7: Compare main company vs competitors
    comparison_summary = summarize_comparison(key_metrics_df, competitor_metrics_df)
    print("\nComparison Summary:\n", comparison_summary)

    # Step 8: Extract and summarize earnings call transcript
    transcript_path = input("\nEnter the path to the earnings call transcript PDF: ")
    transcript_text = Data_retreival.extract_text_from_pdf(transcript_path)
    
    transcript_summary = summarize_text(transcript_text, context="earnings call transcript")
    print("\nEarnings Call Transcript Summary:\n", transcript_summary)


if __name__ == "__main__":
    main()
