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

st.dataframe(df)

st.markdown("Please choose a dashboard using the sidebar on the left.")
