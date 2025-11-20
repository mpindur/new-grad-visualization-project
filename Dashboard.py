import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

st.header("_Recent Graduates_ :red[Data]")

st.markdown("A series of interactive dashboards to support exploration of the recent graduate dataset.")

st.markdown("This is the raw data used to produce the dashboard:")

df = pd.read_csv("data/raw_graduates.csv")

# ---------------------
# Sidebar filters
# ---------------------
st.sidebar.header("Filters")

# Map friendly degree names to the CSV column names present in the dataset
degree_map = {
	"All": None,
	"Bachelors": "Education.Degrees.Bachelors",
	"Masters": "Education.Degrees.Masters",
	"Doctorates": "Education.Degrees.Doctorates",
	"Professionals": "Education.Degrees.Professionals",
}

selected_degree = st.sidebar.selectbox("Degree", list(degree_map.keys()), index=1)

# Apply degree filter. Note: this dataset stores counts by degree in columns
# (e.g. Education.Degrees.Bachelors) rather than a single categorical column.
# Here we treat a row as relevant to a degree if the corresponding degree
# column value is > 0. This is a conservative, easy-to-understand filter.
if degree_map[selected_degree] is None:
	filtered_df = df.copy()
else:
	col = degree_map[selected_degree]
	if col not in df.columns:
		st.warning(f"Degree column {col} not found in dataset. Showing all rows.")
		filtered_df = df.copy()
	else:
		# Keep rows where there were graduates with the chosen degree
		filtered_df = df[df[col].fillna(0) > 0]

st.markdown("Please choose a dashboard using the sidebar on the left.")

# Quick summary for the selected degree
st.subheader(f"Data preview — Degree: {selected_degree}")
st.write(f"Rows matching filter: {len(filtered_df):,}")

# Show a small summary metric (median of the reported median salary for the filtered rows)
if "Salaries.Median" in filtered_df.columns:
	try:
		median_salary = filtered_df["Salaries.Median"].replace({0: np.nan}).dropna().median()
		if np.isfinite(median_salary):
			st.metric(label="Median salary (median of rows)", value=f"${median_salary:,.0f}")
		else:
			st.info("Median salary not available for the selection.")
	except Exception:
		st.info("Could not compute median salary for the selection.")

st.dataframe(filtered_df)


