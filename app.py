# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from sqlalchemy import create_engine
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import boto3
from pdf2image import convert_from_bytes
import pytesseract
import tempfile
import datetime

st.set_page_config(page_title="Denial Prediction Dashboard", layout="wide")
st.title("🧠 Denial Prediction & Claims Intelligence Dashboard")

user_password = st.secrets.get("dashboard_password", "admin123")
password = st.text_input("Enter Dashboard Password:", type="password")
if password != user_password:
    st.warning("Enter the correct demo password to continue.")
    st.stop()

DATABASE_URL = st.secrets.get("database_url", "postgresql://user:password@localhost/dbname")
engine = create_engine(DATABASE_URL)
summary_df = pd.read_sql("SELECT * FROM denial_prediction_summary", con=engine)
claim_df = pd.read_sql("SELECT * FROM random_forest_denial_predictions", con=engine)
deposit_data = pd.read_csv("simulated_bank_deposits.csv") if os.path.exists("simulated_bank_deposits.csv") else pd.DataFrame()

tabs = st.tabs(["📊 Overview", "📁 Claims", "🔄 Reconciliation", "🚨 Exceptions", "📤 Export ERA", "📌 RCM Tool Comparison", "🧪 Middleware Walkthrough"])

st.sidebar.header("🔍 Filter Options")
unique_payers = summary_df['Payer'].unique()
unique_cpts = summary_df['CPT Code'].unique()
selected_payers = st.sidebar.multiselect("Select Payers", unique_payers, default=list(unique_payers))
selected_cpts = st.sidebar.multiselect("Select CPT Codes", unique_cpts, default=list(unique_cpts))
filtered_summary = summary_df[(summary_df['Payer'].isin(selected_payers)) & (summary_df['CPT Code'].isin(selected_cpts))]
filtered_claims = claim_df[(claim_df['Payer'].isin(selected_payers)) & (claim_df['CPT Code'].isin(selected_cpts))]

st.sidebar.subheader("📂 Upload New ERA or Claim File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
if uploaded_file:
    uploaded_data = pd.read_csv(uploaded_file)
    st.write("📄 Preview of Uploaded Data")
    st.dataframe(uploaded_data.head(), use_container_width=True)
    if 'Billed Amount' in uploaded_data.columns and 'Amount Paid' in uploaded_data.columns:
        uploaded_data['Billed/Paid Ratio'] = uploaded_data['Billed Amount'] / uploaded_data['Amount Paid']
        uploaded_data['Predicted Denial'] = uploaded_data['Billed/Paid Ratio'].apply(lambda x: 1 if x > 1.3 else 0)
        st.write("📊 Inline Denial Predictions")
        st.dataframe(uploaded_data[['Claim ID', 'Payer', 'Billed Amount', 'Amount Paid', 'Predicted Denial']], use_container_width=True)

st.sidebar.subheader("🧪 Demo Files")
st.sidebar.download_button("📥 Download Sample ERA (835)", data="ISA*00*          *00*          *ZZ*ABC123         *ZZ*INSURER999    *...~", file_name="sample_era.edi", mime="text/plain")
if os.path.exists("sample_eob.pdf"):
    with open("sample_eob.pdf", "rb") as f:
        st.sidebar.download_button("📥 Download Sample EOB (PDF)", data=f.read(), file_name="sample_eob.pdf", mime="application/pdf")

with tabs[0]:
    st.subheader("📊 Predicted Denials Summary")
    denial_counts = filtered_claims['Predicted Denial'].value_counts().rename({0: "Not Denied", 1: "Predicted Denied"})
    st.bar_chart(denial_counts)
    denial_pie_data = denial_counts.reset_index()
    denial_pie_data.columns = ['Denial Type', 'Count']
    st.plotly_chart(px.pie(denial_pie_data, names='Denial Type', values='Count', title='Predicted Denials vs Non-Denials'), use_container_width=True)

with tabs[1]:
    st.subheader("📁 All Claims")
    st.dataframe(filtered_claims, use_container_width=True)

with tabs[2]:
    st.subheader("🔄 Reconciliation View")
    st.dataframe(deposit_data.head(), use_container_width=True)

with tabs[3]:
    st.subheader("🚨 Exceptions")
    exceptions = filtered_claims[filtered_claims['Predicted Denial'] == 1]
    st.dataframe(exceptions, use_container_width=True)

with tabs[4]:
    st.subheader("📤 Export ERA File")
    st.text("Coming soon: Generate 835 files from processed results.")

with tabs[5]:
    st.subheader("📌 RCM Platform Comparison")
    vendors = ["Your Platform", "LQpay", "Rectangle Health", "Waystar"]
    features = [
        "EOB / ERA Parsing", "Paper EOB OCR", "Bank Deposit Reconcile", "OpenEMR Integration",
        "Real-Time CC Payments", "Patient Wallet / Portal", "AI Denial Prediction", "Estimated ROI / Savings"
    ]
    feature_map = {
        "Your Platform":     ["✅", "✅", "✅", "✅", "❌", "⚠️ Planned", "✅", "$15k+/mo savings"],
        "LQpay":             ["❌", "❌", "❌", "❌", "✅", "✅", "❌", "$5k+/mo collected faster"],
        "Rectangle Health":  ["❌", "❌", "❌", "❌", "✅", "✅", "❌", "$3k+/mo efficiency gain"],
        "Waystar":           ["✅", "❌", "❌ Limited", "❌", "✅", "✅", "❌", "$10k+/mo on large clinics"]
    }
    df_matrix = pd.DataFrame(feature_map, index=features)
    selected_cols = st.multiselect("Select RCM Vendors to Compare:", vendors, default=vendors)
    filtered_matrix = df_matrix[selected_cols]
    st.dataframe(filtered_matrix.style.highlight_max(axis=0), use_container_width=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="RCM Tool Comparison", ln=True, align="C")
    for index, row in filtered_matrix.iterrows():
        pdf.cell(200, 10, txt=f"{index}: {' | '.join(row)}", ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    pdf_bytes = buffer.getvalue()
    st.download_button("📄 Download PDF", data=pdf_bytes, file_name="rcm_tool_comparison.pdf", mime="application/pdf")

with tabs[6]:
    st.header("🧪 Middleware Walkthrough")
    walkthrough_tabs = st.tabs(["Ingest", "Parse", "Map", "Reconcile", "Exceptions", "Export"])

    with walkthrough_tabs[0]:
        edi_file = st.file_uploader("Upload ERA File", type=["txt", "edi"], key="ingest_edi")
        pdf_file = st.file_uploader("Upload EOB PDF", type="pdf", key="ingest_pdf")
        if edi_file:
            raw_edi = edi_file.read().decode("utf-8", errors="ignore")
            st.text_area("Raw EDI Preview", raw_edi[:500] + "[...]", height=200)
        if pdf_file:
            pdf_bytes = pdf_file.read()
            page = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)[0]
            st.image(page, caption="Scanned EOB Preview", use_column_width=True)
            text = pytesseract.image_to_string(page)
            st.text_area("Extracted OCR Text", text[:1000])

    with walkthrough_tabs[1]:
        st.write("Coming soon: Smart Parsing of 835 + OCR Layout AI")

    with walkthrough_tabs[2]:
        st.write("Coming soon: Fee Mapping and Validation")

    with walkthrough_tabs[3]:
        st.write("Coming soon: Reconciliation against Bank Deposits")

    with walkthrough_tabs[4]:
        st.write("Coming soon: Exception Detection and Alerts")

    with walkthrough_tabs[5]:
        st.write("Coming soon: Export Cleaned + Mapped Claims")

st.sidebar.markdown("---")
st.sidebar.metric("Total Claims", int(filtered_claims.shape[0]))
st.sidebar.metric("Predicted Denials", int(filtered_claims['Predicted Denial'].sum()))
st.sidebar.metric("Actual Denials", int(filtered_claims['Actual Denial'].sum()))

st.markdown("---")
st.markdown(f"Dashboard updated on **{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
