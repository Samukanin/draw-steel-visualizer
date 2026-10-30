import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Draw Steel Ability Visualizer", layout = "wide")

@st.cache_data
def load_data(path:str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding = "utf-8-sig")

    df.columns = [c.strip().rstrip(":").strip() for c in df.columns]
    df = df.rename(columns= {
        "Source Category": "Category",
        "Sub-Source": "Subclass",
        "Power Roll +": "Roll Characteristic",
        "Low": "Tier 1",
        "Med": "Tier 2",
        "High": "Tier 3",
    })

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip()
    df["Subclass"] = (
        df["Subclass"]
        .replace({"-": None, "--": None})
        .fillna("None / General")
    )
    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")
    return df

# Loading Data, and making separate tables for classes vs kits
df = load_data("draw_steel_ability_data.csv")
classes_df = df[df["Category"] == "Class"]
kits_df = df[df["Category"] == "Kit"]

st.title("Draw Steel Ability Data Visualizer!")
st.subheader("By Samuel Galan!")

st.sidebar.header("Class Filters")
all_classes = sorted(classes_df["Source Name"].unique())
selected_classes = st.sidebar.multiselect("Class", all_classes, default=all_classes)

# Subclass options depending on which classes are selected
subclass_options = sorted(
    classes_df[classes_df["Source Name"].isin(selected_classes)]["Subclass"].unique()
)
selected_subclasses = st.sidebar.multiselect(
    "Subclass", subclass_options, default=subclass_options
)

filtered = classes_df[
    classes_df["Source Name"].isin(selected_classes)
    & classes_df["Subclass"].isin(selected_subclasses)
]


# Tabs ------------------
overview, data_tab, charts_tab, insights = st.tabs(
    ["Overview", "Data", "Charts", "Insights"]
)

# Overview ------------------
with overview:
    st.header("Overview")
    st.write(
        "This app was made as a way to visualize data from"
        "the many player abilities in tabletop RPG **Draw Steel**"
        "by MCDM Productions! Each row in the dataset is one ability belonging"
        "to a hero class or kit. These aren't the only sources of abilities"
        "in the game, nor have I updated it to include new classes that have"
        "come out since its release, but it's a start!"
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Total abilities", len(df))
    c2.metric("Class abilities", len(classes_df))
    c3.metric("Kit abilities", len(kits_df))
    st.write(
        "**How to use:** use the filters in the sidebar to choose classes and"
        "subclasses. The Data tab shows tables, the Charts tab shows interactive "
        "Plotly charts, and Insights summarizes the data in question!"
    )

# Data --------------------------------
with data_tab:
    st.header("Data")
    st.subheader("Class Abilities")
    st.write(f"Showing {len(filtered)} of {len(classes_df)} class abilities.")
    class_cols = st.multiselect(
        "Columns to display",
        list(classes_df.columns),
        default = ["Source Name", "Name", "Ability Type", "Cost", "Keywords"],
        key = "class_cols",
    )
    st.dataframe(filtered[class_cols], use_container_width=True)

    st.subheader("Kit abilities")
    st.write("Kits are not tied to a class, so the class filters do not apply here.")
    kit_cols = st.multiselect(
        "Columns to display",
        list(kits_df.columns),
        default=["Source Name", "Name", "Ability Type", "Action Type", "Keywords"],
        key="kit_cols",
    )
    st.dataframe(kits_df[kit_cols], use_container_width=True)

    st.subheader("Descriptive statistics (class abilities)")
    st.dataframe(filtered.describe(include="all"), use_container_width=True)

# ------------- Charts
with charts_tab:
    st.header("Charts")

    if filtered.empty:
        st.warning("No abilities match the current filters. Adjust the sidebar selections.")
    else:
        # ---- Bar chart: frequency of an attribute, split by class
        st.subheader("Attribute frequency per class")
        attribute = st.selectbox(
            "Ability attribute",
            ["Keywords", "Ability Type", "Action Type", "Cost", "Roll Characteristic"],
        )
        barmode = st.radio("Bar style", ["group", "stack"], horizontal=True)

        bar_df = filtered[["Source Name", attribute]].dropna()
        if attribute == "Keywords":
            # Keywords are comma-separated, so split into one row per keyword
            bar_df = bar_df.assign(Keywords=bar_df["Keywords"].str.split(",")).explode("Keywords")
            bar_df["Keywords"] = bar_df["Keywords"].str.strip()
        if attribute == "Cost":
            bar_df[attribute] = bar_df[attribute].astype(int).astype(str)

        counts = bar_df.groupby([attribute, "Source Name"]).size().reset_index(name="Count")
        if attribute == "Cost":
            counts = counts.sort_values(attribute, key=lambda s: s.astype(int))
        fig_bar = px.bar(
            counts,
            x=attribute,
            y="Count",
            color="Source Name",
            barmode=barmode,
            title=f"Frequency of {attribute} by Class",
            labels={"Count": "Number of Abilities", "Source Name": "Class"},
        )
        if attribute == "Cost":
            fig_bar.update_xaxes(type="category")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption(
            "Each bar counts abilities with that attribute value. "
            "Colors show which class they belong to."
        )

        # ----- Pie Chart
        st.subheader("Action type distribution")
        pie_choice = st.selectbox(
            "Class for pie chart", ["All selected classes"] + sorted(selected_classes)
        )
        pie_df = filtered if pie_choice == "All selected classes" else filtered[filtered["Source Name"] == pie_choice]
        pie_counts = pie_df["Action Type"].value_counts().reset_index()
        pie_counts.columns = ["Action Type", "Count"]
        fig_pie = px.pie(
            pie_counts,
            names="Action Type",
            values="Count",
            title=f"Action Types: {pie_choice}",
        )
        st.plotly_chart(fig_pie, use_container_width=True)
# Insights ------------------------
with insights:
    st.header("Insights")
    if not filtered.empty:
        top_class = filtered["Source Name"].value_counts().idxmax()
        top_action = filtered["Action Type"].value_counts().idxmax()
        st.write(f"- With the current filters, **{top_class}** has the most abilities.")
        st.write(f"- The most common action type is **{top_action}**.")
    # TODO (Samuel): write your own conclusions here after exploring the charts.
    st.write("Add your own observations here after exploring the charts.")