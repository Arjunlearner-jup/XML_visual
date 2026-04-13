#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from xml.etree import ElementTree as ET

st.set_page_config(page_title="Agricultural Price Indices", layout="wide")

st.title("Effect of Iraq War (03-11) on Agricultural Input and Output Price Indices")

# Read XML file and convert to DataFrame
def xml_to_df(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    rows = []
    for record in root.findall(".//record"):  # adjust if XML tag differs (e.g., ".//item", ".//row")
        row = {}
        for child in record:
            tag = child.tag.strip()
            text = child.text if child.text is not None else ""
            row[tag] = text
        rows.append(row)
    return pd.DataFrame(rows)


df = xml_to_df("AHM02.xml")

# Normalize column names
df.columns = df.columns.str.strip()

df = df.rename(columns={
    "Month": "Month",
    "Agricultural_Product": "Agricultural Product",
    "VALUE": "VALUE"
})

# Ensure numeric type for VALUE
df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
df = df.dropna(subset=["VALUE"])

# Year
df["Year"] = df["Month"].str[:4].astype(int)
# Filter for 2003–2011 and keep the correct column names
df_filtered = df.loc[
    (df["Year"] >= 2003) & (df["Year"] <= 2011),
    ["Year", "Agricultural Product", "VALUE"]
].reset_index(drop=True)




products = sorted(df_filtered["Agricultural Product"].unique())

st.sidebar.header("Filters")
selected_products = st.sidebar.multiselect(
    "Select Agricultural Product",
    products,
    default=products[:5]
)

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df_filtered["Year"].min()),
    max_value=int(df_filtered["Year"].max()),
    value=(2003, 2011)
)

chart_type = st.sidebar.radio(
    "Chart Type",
    ["Line Chart", "Clustered Bar Chart"]
)

filtered = df_filtered[
    (df_filtered["Year"] >= year_range[0]) &
    (df_filtered["Year"] <= year_range[1]) &
    (df_filtered["Agricultural Product"].isin(selected_products))
]

if not filtered.empty:
    df_pivot = filtered.pivot_table(
        index="Year",
        columns="Agricultural Product",
        values="VALUE",
        aggfunc="mean"
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    if chart_type == "Line Chart":
        df_pivot.plot(kind="line", marker="o", linewidth=2, ax=ax)
        ax.set_title("Agricultural Price Indices Over Time")
    else:
        df_pivot.plot(kind="bar", ax=ax)
        ax.set_title("Agricultural Price Indices by Year and Product")

    ax.set_xlabel("Year")
    ax.set_ylabel("Index (Base 2005=100)")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
else:
    st.warning("No data available for the selected filters.")