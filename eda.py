#-----Basic EDA for Customer Churn Dataset-----
"""import pandas as pd

#Load dataset
df = pd.read_csv("data_raw/Customer-Churn-Records 2.csv")
            
 #Basic Info
print("shape:", df.shape)
print("\nColumns: \n", df.columns)

#Data types
print("\nInfo:")
print(df.info())

#Missing values
print("\nMissing Values:")
print(df.isnull().sum())

#Summary stats
print("\nSummary Stats:")
print(df.describe())

#Duplicate check
print("\nDuplicate rows:", df.duplicated().sum())

#Unique values per column
print("\nUnique values:")
for col in df.columns:
    print(col, ":", df[col].nunique())
"""


#-----Advanced EDA for Customer Churn Dataset-----
import pandas as pd
import numpy as np

#Load

df = pd.read_csv("data_raw/Customer-Churn-Records 2.csv")

#-----1) Standardize Columns -------

df.columns = [c.strip().replace(" ", "_") for c in df.columns]

#-----2) Define Churn Column (this dataset uses Exited to represent Churn) -----

if "Exited" in df.columns:
    df["Churn"] = df["Exited"].map( {0: "Retained", 1: "Churned"})
else:
    raise ValueError("Could not find 'Exited' column to define churn.")
    
#-----3) Feature Engineering (senior level segments) -----

df["Age_Band"] = pd.cut (
    df["Age"],
    bins = [17, 25, 35, 45, 55, 65, 120],
    labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "66+"]
)

df["CreditScore_Band"] = pd.cut(
    df["CreditScore"],
    bins = [0, 579, 669, 739, 799, 850, 1000],
    labels = ["Poor(<580)", "Fair(580-669)", "Good(670-739)", "VeryGood(740-799)", "Excellent(800-850)", "850+" ]

)

df["Tenure_Band"] = pd.cut (
    df["Tenure"],
    bins = [-1, 1, 3, 6, 10],
    labels = ["0-1", "2-3", "4-6", "7-10"]
)
df["Balance_Band"] = pd.qcut (
    df["Balance"],
    q=4,
    duplicates="drop"

)

df["Salary_Band"] = pd.qcut(
    df["EstimatedSalary"],
    q=4,
    duplicates="drop"
)

# OPtional if Card Type exists

if "Card_Type" in df.columns:
    df["Card_Type"] = df["Card_Type"].astype(str)

#---- 4) KPI function-------

def churn_rate(d):
    return round(d["Exited"].mean() * 100, 2)

print("\n=========")
print("TOP KPI's")
print("=========")
print("Total Customers:", len(df))
print("Churn Rate (%):", churn_rate(df))
print("Average Balance:", round(df["Balance"].mean(), 2))
print("Average Credit Score:", round(df["CreditScore"].mean(), 2))
print("Active Member %:", round((df["IsActiveMember"].mean() * 100), 2))
print("Churned Customers:", int(df["Exited"].sum()))
print("Retained Customers:", int((df["Exited"] == 0).sum()))

# -------------------------
# 5) Segment churn tables
# -------------------------
def segment_table(col):
    out = (df.groupby(col)
             .agg(customers=("Exited", "count"),
                  churned=("Exited", "sum"),
                  churn_rate_pct=("Exited", lambda x: round(x.mean()*100, 2)))
             .reset_index()
             .sort_values("churn_rate_pct", ascending=False))
    return out

segments = [
    "Geography", "Gender", "Age_Band", "Tenure_Band",
    "NumOfProducts", "IsActiveMember", "HasCrCard",
    "CreditScore_Band", "Balance_Band", "Salary_Band"
]

tables = {}
for s in segments:
    if s in df.columns:
        tables[s] = segment_table(s)
        print(f"\n--- Churn by {s} ---")
        print(tables[s].to_string(index=False))

# -------------------------
# 6) Complaint & Satisfaction impact (if exists)
# -------------------------
if "Complain" in df.columns:
    print("\n--- Churn by Complaint ---")
    print(segment_table("Complain").to_string(index=False))

if "Satisfaction_Score" in df.columns:
    # group satisfaction into bands
    df["Satisfaction_Band"] = pd.cut(df["Satisfaction_Score"], bins=[0, 2, 3, 4, 5], labels=["1-2", "3", "4", "5"])
    print("\n--- Churn by Satisfaction Band ---")
    print(segment_table("Satisfaction_Band").to_string(index=False))

# -------------------------
# 7) Export clean dataset for Tableau
# -------------------------
drop_cols = [c for c in ["RowNumber", "CustomerId", "Surname"] if c in df.columns]
df_export = df.drop(columns=drop_cols)

df_export.to_csv("data_clean/bank_churn_clean.csv", index=False)
print("\n Exported: data_clean/bank_churn_clean.csv")



                            