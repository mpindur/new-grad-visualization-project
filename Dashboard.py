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
			
major_options = sorted(filtered_df['Education.Major'].unique())
major_options.insert(0, "All")

selected_major = st.sidebar.selectbox(
    "Major",
    options=major_options,
    index=0
)

# Apply the major filter to filtered_df
if selected_major != "All":
    filtered_df = filtered_df[filtered_df['Education.Major'] == selected_major]
	
gender_map = {
    "All": None,
    "Female": "Demographics.Gender.Females", # Using plural name for the dataset
    "Male": "Demographics.Gender.Males",     # Using plural name for the dataset
}

selected_gender = st.sidebar.selectbox(
    "Gender",
    list(gender_map.keys()),
    index=0 # Default to 'All'
)

# Apply the gender filter to filtered_df
if gender_map[selected_gender] is not None:
    col = gender_map[selected_gender]
    if col not in filtered_df.columns:
        st.warning(f"Gender column {col} not found in dataset. Showing all rows from previous filter.")
    else:
        # Keep rows where the count in the selected gender column is greater than 0
        filtered_df = filtered_df[filtered_df[col].fillna(0) > 0]

employment_map = {
    "All": None,
    "Employed": "Employment.Status.Employed",
    "Unemployed": "Employment.Status.Unemployed",
    "Not in Labor Force": "Employment.Status.Not in Labor Force",
}

selected_employment = st.sidebar.selectbox(
    "Employment Status",
    list(employment_map.keys()),
    index=0
)

# Apply the employment filter to filtered_df
if employment_map[selected_employment] is not None:
    col = employment_map[selected_employment]
    if col not in filtered_df.columns:
        st.warning(f"Employment column {col} not found in dataset. Showing all rows from previous filter.")
    else:
        # Keep rows where the count for the selected status is greater than 0
        filtered_df = filtered_df[filtered_df[col].fillna(0) > 0]

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

# ---------------------
# Pie charts: Ethnicity, Gender, Degree type (based on filtered_df)
# ---------------------
def make_pie_chart(labels, values, title):
	import pandas as _pd
	if len(labels) == 0 or sum(values) == 0:
		return None
	pie_df = _pd.DataFrame({"category": labels, "value": values})
	pie_df = pie_df[pie_df["value"] > 0]
	if pie_df.empty:
		return None
	pie_df["pct"] = (pie_df["value"] / pie_df["value"].sum() * 100).round(1)
	chart = alt.Chart(pie_df).mark_arc(innerRadius=20).encode(
		theta=alt.Theta(field="value", type="quantitative"),
		color=alt.Color(field="category", type="nominal", legend=alt.Legend(title=title)),
		tooltip=[alt.Tooltip("category:N", title=title), alt.Tooltip("value:Q", title="Count"), alt.Tooltip("pct:Q", title="%")],
	).properties(width=250, height=250)
	return chart

col1, col2, col3 = st.columns(3)

# Ethnicity pie
eth_prefix = "Demographics.Ethnicity."
eth_cols = [c for c in filtered_df.columns if c.startswith(eth_prefix)]
if eth_cols:
	eth_labels = [c.replace(eth_prefix, "") for c in eth_cols]
	eth_values = filtered_df[eth_cols].fillna(0).sum(axis=0).astype(float).tolist()
	eth_chart = make_pie_chart(eth_labels, eth_values, "Ethnicity")
	with col1:
		st.subheader("Ethnicity")
		if eth_chart is not None:
			st.altair_chart(eth_chart, use_container_width=False)
		else:
			st.info("No ethnicity data to display for the current filter.")
else:
	with col1:
		st.subheader("Ethnicity")
		st.info("Ethnicity columns not found in dataset.")

# Gender pie
gen_prefix = "Demographics.Gender."
gen_cols = [c for c in filtered_df.columns if c.startswith(gen_prefix)]
if gen_cols:
	gen_labels = [c.replace(gen_prefix, "") for c in gen_cols]
	gen_values = filtered_df[gen_cols].fillna(0).sum(axis=0).astype(float).tolist()
	gen_chart = make_pie_chart(gen_labels, gen_values, "Gender")
	with col2:
		st.subheader("Gender")
		if gen_chart is not None:
			st.altair_chart(gen_chart, use_container_width=False)
		else:
			st.info("No gender data to display for the current filter.")
else:
	with col2:
		st.subheader("Gender")
		st.info("Gender columns not found in dataset.")

# Degree type pie
deg_prefix = "Education.Degrees."
deg_cols = [c for c in filtered_df.columns if c.startswith(deg_prefix)]
if deg_cols:
	deg_labels = [c.replace(deg_prefix, "") for c in deg_cols]
	deg_values = filtered_df[deg_cols].fillna(0).sum(axis=0).astype(float).tolist()
	deg_chart = make_pie_chart(deg_labels, deg_values, "Degree Type")
	with col3:
		st.subheader("Degree type")
		if deg_chart is not None:
			st.altair_chart(deg_chart, use_container_width=False)
		else:
			st.info("No degree data to display for the current filter.")
else:
	with col3:
		st.subheader("Degree type")
		st.info("Degree columns not found in dataset.")

st.dataframe(filtered_df)


major_counts = filtered_df.groupby("Education.Major")["Demographics.Total"].sum().reset_index()
major_counts.columns = ["Major", "Count"]

total_females = filtered_df["Demographics.Gender.Females"].sum()
total_males = filtered_df["Demographics.Gender.Males"].sum()

gender_data = {
    "Category": ["Female", "Male"],
    "Count": [total_females, total_males],
}
gender_counts = pd.DataFrame(gender_data)

major_base = alt.Chart(major_counts).encode(
    theta=alt.Theta("Count:Q", stack=True)
).transform_joinaggregate(
    TotalGraduates='sum(Count)',
    groupby=[]
).transform_calculate(
    Percentage="datum.Count / datum.TotalGraduates"
)

# Outer Pie Marks (Donut shape)
outer_pie = major_base.mark_arc(outerRadius=120, innerRadius=80).encode(
    color=alt.Color("Major:N"),
    order=alt.Order("Count:Q", sort="descending"),
    tooltip=[
        "Major:N",
        alt.Tooltip("Count:Q", format=","),
        alt.Tooltip("Percentage:Q", format=".1%", title="Proportion")
    ]
)

# Outer Text Labels (showing percentages)
outer_text = major_base.mark_text(radius=135).encode(
    text=alt.Text("Percentage:Q", format=".1%"),
    order=alt.Order("Count:Q", sort="descending"),
    color=alt.value("black")
).transform_filter(
    # Filter out labels for slices smaller than 3%
    alt.datum.Percentage > 0.03
)


# --- Inner Ring (Gender) ---

# Base chart with transformations to calculate percentages
gender_base = alt.Chart(gender_counts).encode(
    theta=alt.Theta("Count:Q", stack=True)
).transform_joinaggregate(
    TotalGenderCount='sum(Count)',
    groupby=[]
).transform_calculate(
    Percentage="datum.Count / datum.TotalGenderCount"
)

# Inner Pie Marks (Solid circle)
inner_pie = gender_base.mark_arc(outerRadius=70, innerRadius=0).encode(
    # Custom colors to distinguish gender from major colors
    color=alt.Color("Category:N", scale=alt.Scale(range=['#e7968a', '#8ec7e8'])),
    order=alt.Order("Count:Q", sort="descending"),
    tooltip=[
        "Category:N",
        alt.Tooltip("Count:Q", format=","),
        alt.Tooltip("Percentage:Q", format=".1%", title="Proportion")
    ]
)

# --- Combine Layers ---
chart = (inner_pie + outer_pie + outer_text).properties(
    title=f"Graduate Breakdown by Major and Overall Gender Split").interactive() # Allows zooming and panning

st.altair_chart(chart)