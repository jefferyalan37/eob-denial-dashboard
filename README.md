readme_content = """
# EOB Denial Prediction & Claims Intelligence Dashboard

A Streamlit app designed to demo AI-enhanced automation of claim denial detection, reconciliation, and exception management for healthcare and dental RCM.

---

## 📁 Files

| File                          | Purpose                                              |
|-------------------------------|------------------------------------------------------|
| `app.py`                      | Streamlit dashboard code                            |
| `claims.csv`                  | Raw dental claims (CDT codes, billed, paid, etc.)   |
| `simulated_bank_deposits.csv`| Bank deposit entries for reconciliation             |
| `summary.csv`                 | Preprocessed summary for fast filtering + metrics   |
| `requirements.txt`           | App dependencies                                    |

---

##  Demo Instructions

1. Clone or upload to [Streamlit Cloud](https://share.streamlit.io).
2. Drop all CSVs into the project root.
3. Launch the app to:
   - View denial predictions
   - Run reconciliation
   - Inspect flagged exceptions
   - Export stubbed ERA

---

##  Features

- CPT/CDT-based denial prediction using heuristics
- Reconciliation logic for bank mismatch detection
- Interactive filters by payer and procedure code
- Upload new CSVs or sample 835/EOB PDFs
- PDF-to-claim OCR parsing module (WIP)

---

Built to simulate RCM modernization for institutional demo use cases (PNC Bank, DSOs, dental networks).
"""

readme_path = "/mnt/data/README.md"
with open(readme_path, "w") as f:
    f.write(readme_content)

readme_path
