import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import Data_retrieval  # Import your data retrieval module
from summarizer import summarize_text, summarize_financial_metrics, summarize_comparison
from config import GEMINI_API_KEY
import google.generativeai as genai


genai.configure(api_key=GEMINI_API_KEY)

# Streamlit Page Configuration
st.set_page_config(page_title='FinSight AI', page_icon='📊', layout='wide')
st.title("📊 FinSight AI - Financial Analysis Dashboard")

# File Upload
uploaded_file = st.file_uploader("Upload Financial Report PDF", type=['pdf'])
if uploaded_file:
    with st.spinner("Extracting data..."):
        report_text = Data_retrieval.extract_text_from_pdf(uploaded_file)
        company_name = Data_retrieval.extract_company_name_llm(report_text,api_key=GEMINI_API_KEY)
        key_metrics = Data_retrieval.extract_key_metrics_llm(report_text)
        key_metrics_df = Data_retrieval.json_to_dataframe(key_metrics)
    
    st.subheader(f"📌 {company_name} - Key Financial Metrics")
    st.dataframe(key_metrics_df)
    
    # Financial Summary
    st.subheader("📋 Financial Summary")
    report_summary = summarize_text(report_text, context="financial report")
    st.write(report_summary)
    
    financial_summary = summarize_financial_metrics(key_metrics_df)
    st.write(financial_summary)
    
    # Competitor Analysis
    competitors_input = st.text_input("Enter competitor company names (comma-separated):")
    if competitors_input:
        competitors = [c.strip() for c in competitors_input.split(",") if c]
        competitor_data = Data_retrieval.fetch_data(company_name, competitors)
        competitor_metrics_df = Data_retrieval.json_to_dataframe(competitor_data["competitors"])
        
        st.subheader("🏆 Competitor Benchmarking")
        st.dataframe(competitor_metrics_df)
        
        comparison_summary = summarize_comparison(key_metrics_df, competitor_metrics_df)
        st.write(comparison_summary)
    
    # Visualization
    st.subheader("📈 Data Visualization")
    selected_metric = st.selectbox("Select a metric to visualize", key_metrics_df['Metric'].unique())
    if selected_metric:
        fig = px.line(key_metrics_df[key_metrics_df['Metric'] == selected_metric], x='Year', y='Value', title=f"{selected_metric} Over Time")
        st.plotly_chart(fig)
    
    # PDF Export
    def generate_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"{company_name} - Financial Report Summary", ln=True, align='C')
        pdf.multi_cell(0, 10, report_summary)
        return pdf.output(dest='S').encode('latin1')
    
    if st.button("📄 Download PDF Report"):
        pdf_data = generate_pdf()
        st.download_button(label="Download Report", data=pdf_data, file_name=f"{company_name}_Report.pdf", mime="application/pdf")
    
    # PPT Export Placeholder
    st.button("📊 Export to PowerPoint (Coming Soon)")
