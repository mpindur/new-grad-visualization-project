import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

st.title("Demographics")
st.markdown("This interactive dashboard supports the exploration of the demographics (age, gender, and race) of the people involved in fatal accidental overdoses in Allegheny County.  You can filter by the year of the overdose incident, as well as the primary drug present in the incident.")

df = pd.read_csv("data/overdose_data_092525.csv")
df.death_date_and_time = pd.to_datetime(df.death_date_and_time)

# to make the visualizations more meaningful, we unabbreviate the race and sex columns

df['race'] = df['race'].str.replace('W','White')
df['race'] = df['race'].str.replace('B','Black')
df['race'] = df['race'].str.replace('H|A|I|M|O|U','Other', regex=True) #there are very few non-white/back decedents in this dataset, so we merge the remaining categories to 'other'
df.dropna(subset = ['race'], inplace=True)  #get rid of nulls

df['sex'] = df['sex'].str.replace('M','Male')
df['sex'] = df['sex'].str.replace('F','Female')

st.subheader("Filters")

#insert filters here
col1, col2 = st.columns(2)
with col1:
    min_year = int(df['case_year'].min())
    max_year = int(df['case_year'].max())

    year_range = st.slider(
        "Filter by Year",
        min_value = min_year,
        max_value = max_year,
        value=(min_year, max_year)
    )

with col2:
    drug_choices = st.multiselect(
        "Filter by the primary drug present",
        options=df['combined_od1'].unique(),
        default=[]  
    )


filtered_df = df[
        df['case_year'].between(*year_range) &
        (df['combined_od1'].astype(str).isin(drug_choices) if drug_choices else True)
    ]


st.subheader("Visualizations")

#insert visualizations here

year_counts = filtered_df["case_year"].value_counts().reset_index(name="count")

hist_chart_yr = alt.Chart(year_counts).mark_bar().encode(
    alt.X('case_year:O',sort="ascending").title("Year"),
    alt.Y('count:Q').title("Count of Fata Overdoses"),
    tooltip=["case_year","count"]
).properties(
        title="Year",
        height=300
    )

st.altair_chart(hist_chart_yr, use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:

    age_counts = filtered_df["age"].value_counts().reset_index(name="count")

    hist_chart_age = alt.Chart(age_counts).mark_bar().encode(
        alt.Y('age:O',sort="descending",axis=alt.Axis(values=[0, 50, 100])).title(""),
        alt.X('count:Q').title("Count of Fatal Overdoses"),
        tooltip=["age","count"]
    ).properties(
            title="Age",
            height=200
        )
    
    st.altair_chart(hist_chart_age, use_container_width=True)

with col2:
    gender_counts = filtered_df["sex"].value_counts().reset_index(name="count")

    bar_chart_sex = alt.Chart(gender_counts).mark_bar().encode(
        alt.X('count:Q', axis=alt.Axis(values=[0, 2000, 4000])).title("Count of Fatal Overdoses"),
        alt.Y('sex:N').title(""),
        tooltip=["count", "sex"]
    ).properties(
            title="Gender",
            height=200
        )

    st.altair_chart(bar_chart_sex, use_container_width=True)

with col3:
    filtered_df["race_binned"] = filtered_df["race"].apply(
        lambda x: "White" if x == "White"
        else "Black" if x == "Black"
        else "Other"
    )

    race_counts = filtered_df["race_binned"].value_counts().reset_index(name="count")

    bar_chart_race = alt.Chart(race_counts).mark_bar().encode(
        alt.X('count:Q').title("Count of Fatal Overdoses"),
        alt.Y('race_binned:N').title(""),
        tooltip=["count", "race_binned"]
    ).properties(
            title="Race",
            height=200
        )

    st.altair_chart(bar_chart_race, use_container_width=True)