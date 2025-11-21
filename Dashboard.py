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

# Employment Status pie
emp_cols = ["Employment.Status.Employed", "Employment.Status.Unemployed", "Employment.Status.Not in Labor Force"]
if all(c in filtered_df.columns for c in emp_cols):
    emp_labels = ["Employed", "Unemployed", "Not in Labor Force"]
    emp_values = filtered_df[emp_cols].fillna(0).sum(axis=0).astype(float).tolist()

    import pandas as _pd
    pie_df = _pd.DataFrame({"category": emp_labels, "value": emp_values})
    pie_df = pie_df[pie_df["value"] > 0]
    pie_df["pct"] = (pie_df["value"] / pie_df["value"].sum() * 100).round(1)

    emp_chart = alt.Chart(pie_df).mark_arc(innerRadius=40).encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="category", type="nominal", legend=alt.Legend(title="Employment Status")),
        tooltip=[alt.Tooltip("category:N", title="Employment Status"), alt.Tooltip("value:Q", title="Count"), alt.Tooltip("pct:Q", title="%")],
    ).properties(width=500, height=500) 

    st.subheader("Employment")
    if emp_chart is not None:
        st.altair_chart(emp_chart, use_container_width=False)
    else:
        st.info("No employment data to display for the current filter.")
else:
    st.subheader("Employment")
    st.info("Required employment columns not found in dataset.")

st.markdown("---")
st.subheader("Employment Details Selector")

# New Selector Widget to control visibility based on user request
selected_status = st.selectbox(
    "Select an employment status to view related details:", 
    options=["Select Status", "Employed", "Unemployed", "Not in Labor Force"],
    index=0
)
st.markdown("---")

# Employment details
def make_horizontal_bar_chart(labels, values, title, category_label, count_label):
    import pandas as _pd
    
    if len(labels) == 0 or sum(values) == 0:
        return None
    
    bar_df = _pd.DataFrame({category_label: labels, count_label: values})
    bar_df = bar_df[bar_df[count_label] > 0]
    
    if bar_df.empty:
        return None

    chart = alt.Chart(bar_df).mark_bar().encode(
        x=alt.X(count_label, title="Count", axis=alt.Axis(format=",")),
        y=alt.Y(category_label, sort='-x', title=category_label),
        tooltip=[
            alt.Tooltip(category_label, title=category_label), 
            alt.Tooltip(count_label, title="Count", format=",")
        ]
    ).properties(title=title, width="container").interactive()
    
    return chart

st.subheader("Employment Details")
if selected_status == "Unemployed":
	reason_prefix = "Employment.Reason for Not Working."
	reason_cols = [c for c in filtered_df.columns if c.startswith(reason_prefix)]

	# Employment Reason for Not Working
	st.subheader("Reason for Not Working")
	if reason_cols:
		reason_labels = [c.replace(reason_prefix, "") for c in reason_cols]
		reason_values = filtered_df[reason_cols].fillna(0).sum(axis=0).astype(float).tolist()
		reason_title = "Reason for Not Working"
			
		reason_chart = make_pie_chart(reason_labels, reason_values, reason_title)
			
		if reason_chart is not None:
			st.altair_chart(reason_chart, use_container_width=False) 
		else:
			st.info("No 'Reason for Not Working' data to display for the current filter.")
	else:
		st.info("Reason for Not Working columns not found in dataset.")


# Employment Work Activity
elif selected_status == "Employed":
	activity_prefix = "Employment.Work Activity."
	activity_cols = [c for c in filtered_df.columns if c.startswith(activity_prefix)]

	st.subheader("Work Activity")
	if activity_cols:
		activity_labels = [c.replace(activity_prefix, "") for c in activity_cols]
		activity_values = filtered_df[activity_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=0).astype(int).tolist()
		activity_title = ""

		top_df = pd.DataFrame({
			"Activity": activity_labels, 
			"Count": activity_values
		})

		top_df = top_df[top_df["Count"] > 0].sort_values(by="Count", ascending=False).head(3)

		if not top_df.empty:
			top_3_numbered_list = []
			rank = 1
			for index, row in top_df.iterrows():
				top_3_numbered_list.append(f"{rank}. {row['Activity']}")
				rank += 1
			
			st.markdown(f"**Top 3**")
			st.markdown("\n".join(top_3_numbered_list))

		activity_chart = make_horizontal_bar_chart(activity_labels, activity_values, activity_title, "Activity", "Count")
		
		if activity_chart is not None:
			st.altair_chart(activity_chart, use_container_width=True)
			
		else:
			st.info("No 'Work Activity' data to display for the current filter.")
	else:
		st.info("Work Activity columns not found in dataset.")

	st.subheader("Field Alignment")
	col6, col7 = st.columns(2)

	outside_field_prefix = "Employment.Reason Working Outside Field."
	outside_field_cols = [c for c in filtered_df.columns if c.startswith(outside_field_prefix)]

	with col6:
		st.subheader("Working In vs. Outside Field")
		if outside_field_cols:
			outside_count = filtered_df[outside_field_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=0).sum().astype(int)
		else:
			outside_count = 0
		
		employed_col = "Employment.Status.Employed"
		if employed_col in filtered_df.columns:
			employed_total = filtered_df[employed_col].apply(pd.to_numeric, errors='coerce').fillna(0).sum().astype(int)
			in_field_count = max(0, employed_total - outside_count)
		else:
			in_field_count = 0
		
		field_labels = ["Working in Field", "Working Outside Field"]
		field_values = [in_field_count, outside_count]

		field_chart = make_pie_chart(field_labels, field_values, "Field Alignment")

		if field_chart is not None and (in_field_count > 0 or outside_count > 0):
			st.altair_chart(field_chart, use_container_width=False)
		else:
			st.info("Employment Status or Outside Field reason columns are missing or data is zero.")

	with col7:
		st.subheader("Reasons for Working Outside Field")
		
		if outside_field_cols:
			reason_labels = [c.replace(outside_field_prefix, "") for c in outside_field_cols]
			reason_values = filtered_df[outside_field_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=0).astype(int).tolist()
			reason_title = ""

			reason_chart = make_horizontal_bar_chart(reason_labels, reason_values, reason_title, "Reason", "Count")
			
			if reason_chart is not None:
				st.altair_chart(reason_chart, use_container_width=True)
			else:
				st.info("No data available for reasons working outside the field.")
		else:
			st.info("Reasons for Working Outside Field columns not found in dataset.")

st.dataframe(filtered_df)


