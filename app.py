# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import boto3
from pdf2image import convert_from_bytes
import pytesseract
import tempfile
import datetime

st.set_page_config(page_title="Denial Prediction Dashboard", layout="wide")
st.title("Denial Prediction & Claims Intelligence Dashboard")

user_password = st.secrets.get("dashboard_password", "admin123")
password = st.text_input("Enter Dashboard Password:", type="password")
if password != user_password:
    st.warning("Enter the correct demo password to continue.")
    st.stop()

summary_df = pd.read_csv("summary.csv") if os.path.exists("summary.csv") else pd.DataFrame()
claim_df = pd.read_csv("claims.csv") if os.path.exists("claims.csv") else pd.DataFrame()
deposit_data = pd.read_csv("simulated_bank_deposits.csv") if os.path.exists("simulated_bank_deposits.csv") else pd.DataFrame()

tabs = st.tabs([" Overview", " Claims", " Reconciliation", " Exceptions", "Export ERA", " RCM Tool Comparison", "Middleware Walkthrough"])

st.sidebar.header(" Filter Options")
unique_payers = summary_df['Payer'].unique() if not summary_df.empty else []
unique_cpts = summary_df['CPT Code'].unique() if not summary_df.empty else []
selected_payers = st.sidebar.multiselect("Select Payers", unique_payers, default=list(unique_payers))
selected_cpts = st.sidebar.multiselect("Select CPT Codes", unique_cpts, default=list(unique_cpts))
filtered_summary = summary_df[(summary_df['Payer'].isin(selected_payers)) & (summary_df['CPT Code'].isin(selected_cpts))] if not summary_df.empty else pd.DataFrame()
filtered_claims = claim_df[(claim_df['Payer'].isin(selected_payers)) & (claim_df['CPT Code'].isin(selected_cpts))] if not claim_df.empty else pd.DataFrame()

st.sidebar.subheader("Upload New ERA or Claim File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
if uploaded_file:
    uploaded_data = pd.read_csv(uploaded_file)
    st.write("Preview of Uploaded Data")
    st.dataframe(uploaded_data.head(), use_container_width=True)
    if 'Billed Amount' in uploaded_data.columns and 'Amount Paid' in uploaded_data.columns:
        uploaded_data['Billed/Paid Ratio'] = uploaded_data['Billed Amount'] / uploaded_data['Amount Paid']
        uploaded_data['Predicted Denial'] = uploaded_data['Billed/Paid Ratio'].apply(lambda x: 1 if x > 1.3 else 0)
        st.write(" Inline Denial Predictions")
        st.dataframe(uploaded_data[['Claim ID', 'Payer', 'Billed Amount', 'Amount Paid', 'Predicted Denial']], use_container_width=True)

st.sidebar.subheader("Demo Files")
st.sidebar.download_button("Download Sample ERA (835)", data="ISA*00*          *00*          *ZZ*ABC123         *ZZ*INSURER999    *...~", file_name="sample_era.edi", mime="text/plain")
if os.path.exists("sample_eob.pdf"):
    with open("sample_eob.pdf", "rb") as f:
        st.sidebar.download_button("Download Sample EOB (PDF)", data=f.read(), file_name="sample_eob.pdf", mime="application/pdf")

with tabs[0]:
    st.subheader(" Predicted Denials Summary")
    if not filtered_claims.empty:
        denial_counts = filtered_claims['Predicted Denial'].value_counts().rename({0: "Not Denied", 1: "Predicted Denied"})
        st.bar_chart(denial_counts)
        denial_pie_data = denial_counts.reset_index()
        denial_pie_data.columns = ['Denial Type', 'Count']
        st.plotly_chart(px.pie(denial_pie_data, names='Denial Type', values='Count', title='Predicted Denials vs Non-Denials'), use_container_width=True)
    else:
        st.write("No claims data available for visualization.")

with tabs[1]:
    st.subheader("All Claims")
    st.dataframe(filtered_claims, use_container_width=True)

with tabs[2]:
    st.subheader("Reconciliation View")
    st.dataframe(deposit_data.head(), use_container_width=True)

with tabs[3]:
    st.subheader("Exceptions")
    exceptions = filtered_claims[filtered_claims['Predicted Denial'] == 1] if not filtered_claims.empty else pd.DataFrame()
    st.dataframe(exceptions, use_container_width=True)

with tabs[4]:
    st.subheader("Export ERA File")
    st.text("Coming soon: Generate 835 files from processed results.")

st.sidebar.markdown("---")
st.sidebar.metric("Total Claims", int(filtered_claims.shape[0]))
st.sidebar.metric("Predicted Denials", int(filtered_claims['Predicted Denial'].sum()) if 'Predicted Denial' in filtered_claims.columns else 0)
st.sidebar.metric("Actual Denials", int(filtered_claims['Actual Denial'].sum()) if 'Actual Denial' in filtered_claims.columns else 0)

st.markdown("---")
st.markdown(f"Dashboard updated on **{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
