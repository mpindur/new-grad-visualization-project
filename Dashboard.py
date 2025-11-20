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

	# ---------------------
	# Year filters (two dropdowns: start and end)
	# - Default is no selection (empty string)
	# - If only start selected -> filter that year
	# - If both selected -> filter inclusive range between start and end

	# Prepare year options from the dataset (only years that actually appear)
	if "Year" in df.columns:
		# coerce to numeric to be safe, drop NaNs, get unique sorted
		years_numeric = pd.to_numeric(df["Year"], errors="coerce").dropna().astype(int)
		present_years = sorted(years_numeric.unique()) if len(years_numeric) > 0 else []
		# keep an empty default option followed by only present years
		year_options = [""] + [str(y) for y in present_years]
	else:
		year_options = [""]

	start_year = st.sidebar.selectbox("From year", year_options, index=0)
	# second dropdown disabled unless the first has a year selected
	end_disabled = (start_year == "")
	# Build end-year options so they cannot be earlier than the selected start year
	if start_year == "":
		end_options = year_options
	else:
		try:
			s_num = int(start_year)
			# only allow end years that are >= start year
			end_options = [""] + [str(y) for y in present_years if y >= s_num]
		except Exception:
			end_options = year_options

	end_year = st.sidebar.selectbox("To year", end_options, index=0, disabled=end_disabled)

	# Apply year filtering to filtered_df (if any selection)
	if start_year != "":
		try:
			s = int(start_year)
			if end_year != "":
				e = int(end_year)
				lo, hi = (min(s, e), max(s, e))
				filtered_df = filtered_df[pd.to_numeric(filtered_df["Year"], errors="coerce").between(lo, hi)]
			else:
				# only start year selected -> exact match
				filtered_df = filtered_df[pd.to_numeric(filtered_df["Year"], errors="coerce").fillna(-9999).astype(int) == s]
		except Exception:
			st.warning("Could not apply year filter due to unexpected Year values.")

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


