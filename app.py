import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Generate claims.csv
n_claims = 50
claim_ids = [f"CLM{str(i).zfill(4)}" for i in range(n_claims)]
payers = ["Aetna", "Cigna", "Guardian", "MetLife", "Delta Dental"]
cdt_codes = ["D0120", "D1110", "D2740", "D2950", "D4341", "D7210"]
billed_amounts = np.random.randint(100, 2000, size=n_claims)
paid_amounts = [amt if random.random() > 0.3 else amt * random.uniform(0.2, 0.8) for amt in billed_amounts]
actual_denials = [0 if paid == billed else 1 for paid, billed in zip(paid_amounts, billed_amounts)]
predicted_denials = [1 if billed / (paid if paid else 1) > 1.3 else 0 for billed, paid in zip(billed_amounts, paid_amounts)]
dates = [(datetime.now() - timedelta(days=random.randint(0, 60))).strftime('%Y-%m-%d') for _ in range(n_claims)]

claims_df = pd.DataFrame({
    "Claim ID": claim_ids,
    "Payer": [random.choice(payers) for _ in range(n_claims)],
    "CDT Code": [random.choice(cdt_codes) for _ in range(n_claims)],
    "Billed Amount": billed_amounts,
    "Amount Paid": paid_amounts,
    "Actual Denial": actual_denials,
    "Predicted Denial": predicted_denials,
    "Date of Service": dates
})

# Generate summary.csv
summary_df = claims_df.groupby(["Payer", "CDT Code"]).agg(
    Total_Claims=("Claim ID", "count"),
    Total_Billed=("Billed Amount", "sum"),
    Total_Paid=("Amount Paid", "sum"),
    Actual_Denials=("Actual Denial", "sum"),
    Predicted_Denials=("Predicted Denial", "sum")
).reset_index()

# Generate simulated_bank_deposits.csv
deposit_dates = [datetime.now() - timedelta(days=random.randint(1, 60)) for _ in range(n_claims)]
deposit_ids = [f"DEP{str(i).zfill(4)}" for i in range(n_claims)]
deposit_amounts = [paid + random.uniform(-10, 10) for paid in paid_amounts]
deposit_sources = [random.choice(payers) for _ in range(n_claims)]
methods = ["EFT", "Check", "ACH"]

deposit_df = pd.DataFrame({
    "Deposit ID": deposit_ids,
    "Deposit Date": [d.strftime('%Y-%m-%d') for d in deposit_dates],
    "Payer": deposit_sources,
    "Deposit Amount": deposit_amounts,
    "Method": [random.choice(methods) for _ in range(n_claims)]
})

# Save to CSV
claims_df.to_csv("claims.csv", index=False)
summary_df.to_csv("summary.csv", index=False)
deposit_df.to_csv("simulated_bank_deposits.csv", index=False)

import ace_tools as tools; tools.display_dataframe_to_user(name="Claims Data Preview", dataframe=claims_df.head())
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Generate claims.csv
n_claims = 50
claim_ids = [f"CLM{str(i).zfill(4)}" for i in range(n_claims)]
payers = ["Aetna", "Cigna", "Guardian", "MetLife", "Delta Dental"]
cdt_codes = ["D0120", "D1110", "D2740", "D2950", "D4341", "D7210"]
billed_amounts = np.random.randint(100, 2000, size=n_claims)
paid_amounts = [amt if random.random() > 0.3 else amt * random.uniform(0.2, 0.8) for amt in billed_amounts]
actual_denials = [0 if paid == billed else 1 for paid, billed in zip(paid_amounts, billed_amounts)]
predicted_denials = [1 if billed / (paid if paid else 1) > 1.3 else 0 for billed, paid in zip(billed_amounts, paid_amounts)]
dates = [(datetime.now() - timedelta(days=random.randint(0, 60))).strftime('%Y-%m-%d') for _ in range(n_claims)]

claims_df = pd.DataFrame({
    "Claim ID": claim_ids,
    "Payer": [random.choice(payers) for _ in range(n_claims)],
    "CDT Code": [random.choice(cdt_codes) for _ in range(n_claims)],
    "Billed Amount": billed_amounts,
    "Amount Paid": paid_amounts,
    "Actual Denial": actual_denials,
    "Predicted Denial": predicted_denials,
    "Date of Service": dates
})

# Generate summary.csv
summary_df = claims_df.groupby(["Payer", "CDT Code"]).agg(
    Total_Claims=("Claim ID", "count"),
    Total_Billed=("Billed Amount", "sum"),
    Total_Paid=("Amount Paid", "sum"),
    Actual_Denials=("Actual Denial", "sum"),
    Predicted_Denials=("Predicted Denial", "sum")
).reset_index()

# Generate simulated_bank_deposits.csv
deposit_dates = [datetime.now() - timedelta(days=random.randint(1, 60)) for _ in range(n_claims)]
deposit_ids = [f"DEP{str(i).zfill(4)}" for i in range(n_claims)]
deposit_amounts = [paid + random.uniform(-10, 10) for paid in paid_amounts]
deposit_sources = [random.choice(payers) for _ in range(n_claims)]
methods = ["EFT", "Check", "ACH"]

deposit_df = pd.DataFrame({
    "Deposit ID": deposit_ids,
    "Deposit Date": [d.strftime('%Y-%m-%d') for d in deposit_dates],
    "Payer": deposit_sources,
    "Deposit Amount": deposit_amounts,
    "Method": [random.choice(methods) for _ in range(n_claims)]
})

# Save to CSV
claims_df.to_csv("claims.csv", index=False)
summary_df.to_csv("summary.csv", index=False)
deposit_df.to_csv("simulated_bank_deposits.csv", index=False)

import ace_tools as tools; tools.display_dataframe_to_user(name="Claims Data Preview", dataframe=claims_df.head())
