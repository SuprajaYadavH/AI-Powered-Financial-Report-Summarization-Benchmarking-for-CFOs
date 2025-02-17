import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from fpdf import FPDF
from sentiment_analyzer import ensemble_sentiment_analysis
from summarizer import summarize_text, summarize_financial_metrics, summarize_comparison, compare_metrics
from Data_retrieval import extract_text_from_pdf, extract_company_name_llm, extract_key_metrics_llm, get_ticker_from_search, fetch_financial_metrics

# Set Page Configuration
st.set_page_config(page_title="Financial Insights Dashboard", layout="wide")

# Sidebar Navigation
st.sidebar.header("📊 FinSight AI")
page = st.sidebar.radio("Navigation", ["Upload Financial Report", "Competitor Comparison", "Sentiment Analysis"])

# Function to create summary cards
def summary_card(title, value, color):
    st.markdown(
        f"""
        <div style="background-color:{color}; padding:15px; border-radius:10px; margin:10px; text-align:center; color:white;">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
        """, unsafe_allow_html=True
    )

if page == "Upload Financial Report":
    st.title("📊 FinSight AI")
    st.subheader("📂 Upload Financial Report PDF")
    uploaded_file = st.file_uploader("Upload a financial report PDF", type=["pdf"])
    
    if uploaded_file:
        report_text = extract_text_from_pdf(uploaded_file)
        company_name = extract_company_name_llm(report_text)
        key_metrics_df = extract_key_metrics_llm(report_text)
        summary_text = summarize_text(report_text, "financial report")
        metrics_summary = summarize_financial_metrics(key_metrics_df)
        
        st.header(f"Company: {company_name}")
        
        # Display Summary Cards
        col1, col2 = st.columns(2)
        col1.markdown("### 📄 Report Summary")
        col1.write(summary_text)
        col2.markdown("### 📊 Key Metrics Summary")
        col2.write(metrics_summary)
        
        # Display Year-wise Key Metrics
        if not key_metrics_df.empty:
            st.markdown("### 📈 Year-over-Year Financial Metrics")
            st.write(key_metrics_df)
            fig = px.line(key_metrics_df, x="Year", y="Value", color="Metric", markers=True)
            st.plotly_chart(fig, use_container_width=True)
    

elif page == "Competitor Comparison":
    st.title("🏆 Competitor Benchmarking")
    if 'company_name' not in locals():
        company_name = st.text_input("Enter Company Name (or upload a report in previous tab)", "")
    competitors = st.text_area("Enter Competitor Names (comma-separated)").split(",")
    
    if st.button("Compare"):
        if company_name and competitors:
            df_comparison = compare_metrics(company_name, competitors)
            main_company_data = df_comparison[df_comparison["Company"] == company_name]
            competitor_data = df_comparison[df_comparison["Company"] != company_name]

            # Display Comparison Table
            st.markdown("### 📊 Financial key metrics Comparison")
            st.write(df_comparison)
          
            st.markdown("### 📋 Competitive Summary")
            st.write(summarize_comparison(main_company_data, competitor_data))
        
            
            # Plot Bar Chart
            fig = px.bar(df_comparison, x="Company", y="Value", color="Metric", barmode="group")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Sentiment Analysis":
    st.title("🔍 Earnings Call Sentiment Analysis")
    transcript_file = st.file_uploader("Upload Earnings Call Transcript PDF (Optional)", type=["pdf"])
    
    if transcript_file:
        transcript_text = extract_text_from_pdf(transcript_file)
        transcript_summary = summarize_text(transcript_text, "earnings call transcript")
        
        st.markdown("### 📄 Earnings Call Summary")
        st.write(transcript_summary)
        
        # Perform Sentiment Analysis
        sentiment_result = ensemble_sentiment_analysis(transcript_text)
        positive_score = sentiment_result["positive"]
        neutral_score = sentiment_result["neutral"]
        negative_score = sentiment_result["negative"]

        # Determine the dominant sentiment
        sentiment_scores = {"Positive": positive_score, "Neutral": neutral_score, "Negative": negative_score}
        dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        dominant_color = {"Positive": "#2ECC71", "Neutral": "#F39C12", "Negative": "#E74C3C"}[dominant_sentiment]

        # Display only the dominant sentiment score
        summary_card(f"{dominant_sentiment} Sentiment", f"{sentiment_scores[dominant_sentiment]}%", dominant_color)

        # Sentiment Distribution Pie Chart
        sentiment_data = pd.DataFrame({
            "Category": ["Positive", "Neutral", "Negative"],
            "Score": [positive_score, neutral_score, negative_score]
        })

        fig = px.pie(sentiment_data, values="Score", names="Category", title="Sentiment Breakdown", 
                     color="Category", color_discrete_map={"Positive": "#2ECC71", "Neutral": "#F39C12", "Negative": "#E74C3C"})
        
        st.plotly_chart(fig, use_container_width=True)

    
st.sidebar.info("AI-Powered Financial Report Summarization & Benchmarking for CFOs")
