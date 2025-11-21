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

# Build majors filter (use Education.Major column)
# If the column exists, populate the multiselect with present majors; include an "All" option
majors_column = "Education.Major"
if majors_column in df.columns:
	majors = sorted(df[majors_column].dropna().astype(str).unique())
	major_options = ["All"] + majors
else:
	majors = []
	major_options = ["All"]

# Allow selecting multiple majors; default to All
selected_majors = st.sidebar.multiselect("Major", major_options, default=["All"]) if len(major_options) > 0 else []

# Start with the full dataframe, then apply filters below
filtered_df = df.copy()

# Apply major filter: keep rows whose Education.Major is in the selected majors
if selected_majors and "All" not in selected_majors:
	if majors_column not in df.columns:
		st.warning(f"Major column {majors_column} not found in dataset. Showing all rows.")
	else:
		try:
			# compare as strings after filling NaNs
			mask = df[majors_column].fillna("").astype(str).isin(selected_majors)
			filtered_df = df[mask].copy()
		except Exception:
			st.warning("Could not apply major filter due to unexpected column values. Showing all rows.")

    

# ---------------------
# Year filters (two dropdowns: start and end) — always visible now
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

# Quick summary for the selected major(s)
# Prepare a label for the selected majors for display
if not selected_majors or "All" in selected_majors:
	majors_label = "All"
else:
	majors_label = ", ".join(selected_majors)

st.subheader(f"Data preview — Major: {majors_label}")
st.write(f"Rows matching filter: {len(filtered_df):,}")

# Compute median salary for later display under the employment chart
median_salary = None
if "Salaries.Median" in filtered_df.columns:
	try:
		_temp_med = filtered_df["Salaries.Median"].replace({0: np.nan}).dropna().median()
		# ensure numeric/finite
		if np.isfinite(_temp_med):
			median_salary = float(_temp_med)
		else:
			median_salary = None
	except Exception:
		median_salary = None

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

# ---------------------
# Employed vs Unemployed donut chart (above the other pie charts)
# ---------------------
try:
	emp_col = "Employment.Status.Employed"
	unemp_col = "Employment.Status.Unemployed"
	emp_sum = 0.0
	unemp_sum = 0.0
	if emp_col in filtered_df.columns:
		emp_sum = float(filtered_df[emp_col].fillna(0).sum())
	if unemp_col in filtered_df.columns:
		unemp_sum = float(filtered_df[unemp_col].fillna(0).sum())

	# Fallback: if explicit Unemployed column missing or zero, try summing reason-for-not-working columns
	if unemp_sum == 0.0:
		reason_prefix = "Employment.Reason for Not Working."
		reason_cols = [c for c in filtered_df.columns if c.startswith(reason_prefix)]
		if reason_cols:
			# sum each row's reasons then total
			unemp_sum = float(filtered_df[reason_cols].fillna(0).sum(axis=1).sum())

	emp_chart = make_pie_chart(["Employed", "Unemployed"], [emp_sum, unemp_sum], "Employment status")
	if emp_chart is not None:
		# center the chart by placing it in the middle column and increase its size
		left_col, center_col, right_col = st.columns([1, 2, 1])
		with center_col:
			# use a centered markdown header with slightly larger text
			st.markdown("<h3 style='text-align:center; margin-bottom: 0.25rem;'>Employment Status</h3>", unsafe_allow_html=True)
			# enlarge the chart by overriding its properties; keep use_container_width=False so sizing is explicit
			st.altair_chart(emp_chart.properties(width=420, height=420), use_container_width=False)
			# show the median salary centered under the donut chart
			# center the block (so it sits under the chart) but left-align the text inside
			try:
				if median_salary is not None:
					st.markdown(
						f"<div style='margin-top:8px; margin-left:auto; margin-right:auto; width:260px;'>"
						f"<div style='font-weight:600; text-align:left;'>Median salary</div>"
						f"<div style='font-size:20px; text-align:left;'>${median_salary:,.0f}</div>"
						f"</div>",
						unsafe_allow_html=True,
					)
				else:
					st.markdown(
						"<div style='margin-top:8px; margin-left:auto; margin-right:auto; width:260px; color:#666; text-align:left;'>Median salary not available for the selection.</div>",
						unsafe_allow_html=True,
					)
			except Exception:
				# fail silently; don't break dashboard rendering
				pass

			# ---------------------
			# Unemployment reasons breakdown table (centered under median)
			# ---------------------
			try:
				reason_prefix = "Employment.Reason for Not Working."
				reason_cols = [c for c in filtered_df.columns if c.startswith(reason_prefix)]
				if reason_cols:
					reasons_series = filtered_df[reason_cols].fillna(0).sum(axis=0)
					reasons_df = pd.DataFrame({
						"reason": [c.replace(reason_prefix, "") for c in reasons_series.index],
						"count": reasons_series.values.astype(float),
					})
					total_reasons = reasons_df["count"].sum()
					if total_reasons > 0:
						# compute simple percent-of-reasons (original behavior)
						reasons_df["percent"] = (reasons_df["count"] / total_reasons * 100).round(1)
						reasons_df = reasons_df.sort_values("count", ascending=False).reset_index(drop=True)
						# center a fixed-width container but left-align the table text
						st.markdown("<div style='margin-left:auto; margin-right:auto; width:360px;'>", unsafe_allow_html=True)
						st.markdown("<div style='font-weight:600; text-align:left; margin-top:8px;'>Unemployment reasons</div>", unsafe_allow_html=True)
						display_df = reasons_df.copy()
						display_df["count"] = display_df["count"].astype(int)
						display_df["percent"] = display_df["percent"].apply(lambda x: f"{x:.1f}%")
						st.table(display_df.rename(columns={"reason": "Reason", "count": "Count", "percent": "Percent"}))
						st.markdown("</div>", unsafe_allow_html=True)
					else:
						st.markdown("<div style='margin-left:auto; margin-right:auto; width:360px; color:#666; text-align:left; margin-top:8px;'>No unemployment reason data available for the selection.</div>", unsafe_allow_html=True)
				else:
					st.markdown("<div style='margin-left:auto; margin-right:auto; width:360px; color:#666; text-align:left; margin-top:8px;'>No unemployment reason columns found in dataset.</div>", unsafe_allow_html=True)
			except Exception:
				# keep dashboard resilient
				pass
	else:
		st.info("Employment status data not available for the current selection.")
except Exception:
	# Don't crash the dashboard for any unexpected data shapes; show a friendly info.
	st.info("Could not compute employment donut chart for the current selection.")

st.subheader("Demographics")
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


