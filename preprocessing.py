import pandas as pd
import numpy as np

def preproc(df):
    df = df[df['Demographics.Total']!=0]

    cols = df.drop(columns = ['Year', 'Education.Major'])

    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df['Year'] = df['Year'].astype("Int64")

    # df["Education.Major"] = df["Education.Major"].astype(str).str.lower().str.strip()

    mean = df["Salaries.Mean"]
    std = df["Salaries.Standard Deviation"]

    z_25 = -0.67449
    z_50 = 0
    z_75 = 0.67449
    z_90 = 1.28155
    z_95 = 1.64485

    df["Salary.P25"] = mean + z_25 * std
    df["Salary.P50"] = mean + z_50 * std
    df["Salary.P75"] = mean + z_75 * std

    df["Salary.Top10.Cutoff"] = mean + z_90 * std
    df["Salary.Top5.Cutoff"]  = mean + z_95 * std

    return df
