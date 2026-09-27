from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Education in Lebanon — 2023", page_icon="🎓", layout="wide")

DATA_FILE = Path(__file__).with_name("Education Level in Lebanon 2023.csv")

EDUCATION_LEVELS = [
    "Illiterate", "Elementary", "Intermediate", "Secondary",
    "Vocational", "University", "Higher_Education"
]

DISPLAY_NAMES = {
    "Illiterate": "Illiterate",
    "Elementary": "Elementary",
    "Intermediate": "Intermediate",
    "Secondary": "Secondary",
    "Vocational": "Vocational",
    "University": "University",
    "Higher_Education": "Higher Education",
}

EDUCATION_COLORS = {
    "Illiterate": "#FFEDA0",
    "Elementary": "#FEB24C",
    "Intermediate": "#FD8D3C",
    "Secondary": "#FC4E2A",
    "Vocational": "#E31A1C",
    "University": "#BD0026",
    "Higher Education": "#800026",
}

PALETTE = [
    "#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C",
    "#FC4E2A", "#E31A1C", "#BD0026", "#800026"
]

GOV_ORDER = [
    "North Lebanon", "Mount Lebanon", "Keserwan-Jbeil", "Bekaa",
    "Nabatieh", "South Lebanon", "Akkar", "Baalbek-Hermel"
]
GOV_COLORS = dict(zip(GOV_ORDER, PALETTE))


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)

    rename_cols = {
        "PercentageofEducationlevelofresidents-illeterate": "Illiterate",
        "PercentageofEducationlevelofresidents-elementary": "Elementary",
        "PercentageofEducationlevelofresidents-intermediate": "Intermediate",
        "PercentageofEducationlevelofresidents-secondary": "Secondary",
        "PercentageofEducationlevelofresidents-vocational": "Vocational",
        "PercentageofEducationlevelofresidents-university": "University",
        "PercentageofEducationlevelofresidents-highereducation": "Higher_Education",
        "PercentageofSchooldropout": "School_Dropout",
    }
    df = df.rename(columns=rename_cols)

    percentage_cols = EDUCATION_LEVELS + ["School_Dropout"]
    for col in percentage_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan

    df["Area"] = (
        df["refArea"].str.split("/").str[-1].str.replace("_", " ", regex=False)
    )

    governorate_map = {
        "Akkar District": "Akkar", "Akkar Governorate": "Akkar",
        "Baalbek District": "Baalbek-Hermel", "Hermel District": "Baalbek-Hermel",
        "Baalbek-Hermel Governorate": "Baalbek-Hermel",
        "Beirut Governorate": "Beirut",
        "Zahle District": "Bekaa", "Western Beqaa District": "Bekaa",
        "Rashaya District": "Bekaa", "Beqaa Governorate": "Bekaa",
        "Keserwan District": "Keserwan-Jbeil", "Byblos District": "Keserwan-Jbeil",
        "Keserwan-Jbeil Governorate": "Keserwan-Jbeil",
        "Aley District": "Mount Lebanon", "Baabda District": "Mount Lebanon",
        "Chouf District": "Mount Lebanon", "Matn District": "Mount Lebanon",
        "Mount Lebanon Governorate": "Mount Lebanon",
        "Bint Jbeil District": "Nabatieh", "Hasbaya District": "Nabatieh",
        "Marjeyoun District": "Nabatieh", "Nabatieh District": "Nabatieh",
        "Nabatieh Governorate": "Nabatieh",
        "Batroun District": "North Lebanon", "Bsharri District": "North Lebanon",
        "Koura District": "North Lebanon", "Miniyeh-Danniyeh District": "North Lebanon",
        "Tripoli District": "North Lebanon", "Zgharta District": "North Lebanon",
        "North Governorate": "North Lebanon",
        "Sidon District": "South Lebanon", "Tyre District": "South Lebanon",
        "Jezzine District": "South Lebanon", "South Governorate": "South Lebanon",
    }
    df["Governorate"] = df["Area"].map(governorate_map)
    return df


def education_profile(data):
    complete = data.dropna(subset=EDUCATION_LEVELS)
    if complete.empty:
        return pd.DataFrame(columns=["Education_Level", "Percentage"])
    profile = complete[EDUCATION_LEVELS].mean().reset_index()
    profile.columns = ["Education_Level", "Percentage"]
    profile["Education_Level"] = profile["Education_Level"].map(DISPLAY_NAMES)
    return profile


def donut_chart(profile, title):
    fig = px.pie(
        profile,
        names="Education_Level",
        values="Percentage",
        hole=0.50,
        color="Education_Level",
        color_discrete_map=EDUCATION_COLORS,
        title=title,
    )
    fig.update_traces(
        textposition="inside",
        texttemplate="%{value:.1f}%",
        hovertemplate="<b>%{label}</b><br>%{value:.2f}%<extra></extra>",
        marker=dict(line=dict(color="white", width=2)),
    )
    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        height=600,
        legend_title="Highest Educational Level Attained",
        margin=dict(l=20, r=20, t=80, b=20),
    )
    return fig


def scatter_chart(data, selected_town):
    scatter = data.dropna(
        subset=["Governorate", "Town", "School_Dropout", "University", "Higher_Education"]
    ).copy()
    scatter["Higher_Education_Attainment"] = scatter["University"] + scatter["Higher_Education"]

    fig = px.scatter(
        scatter,
        x="Higher_Education_Attainment",
        y="School_Dropout",
        color="Governorate",
        color_discrete_map=GOV_COLORS,
        category_orders={"Governorate": GOV_ORDER},
        hover_name="Town",
        hover_data={
            "Governorate": True,
            "Higher_Education_Attainment": ":.2f",
            "School_Dropout": ":.2f",
            "University": ":.2f",
            "Higher_Education": ":.2f",
        },
        labels={
            "Higher_Education_Attainment": "University + Higher Education (%)",
            "School_Dropout": "School Dropout (%)",
        },
        title="School Dropout vs. Higher Education Attainment by Town — 2023",
    )
    fig.update_traces(marker=dict(size=10, opacity=0.55))

    if selected_town != "All towns":
        selected = scatter[scatter["Town"] == selected_town]
        if not selected.empty:
            fig.add_trace(
                go.Scatter(
                    x=selected["Higher_Education_Attainment"],
                    y=selected["School_Dropout"],
                    mode="markers+text",
                    text=selected["Town"],
                    textposition="top center",
                    marker=dict(size=18, color="black", symbol="star", line=dict(color="white", width=2)),
                    name=f"Selected: {selected_town}",
                    hovertemplate=(
                        "<b>%{text}</b><br>University + Higher Education: %{x:.2f}%"
                        "<br>School Dropout: %{y:.2f}%<extra></extra>"
                    ),
                )
            )

    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        height=650,
        xaxis_ticksuffix="%",
        yaxis_ticksuffix="%",
        legend_title="Governorate",
        margin=dict(l=60, r=40, t=80, b=60),
    )
    return fig, scatter


df = load_data()

st.title("Education Levels in Lebanon — 2023")

available_governorates = [g for g in GOV_ORDER if g in df["Governorate"].dropna().unique()]

with st.sidebar:
    st.header("Explore")
    governorate = st.selectbox(
        "Governorate",
        ["All Lebanon"] + available_governorates,
        help="Select a governorate to narrow the analysis."
    )

    if governorate == "All Lebanon":
        governorate_data = df[df["Governorate"].isin(available_governorates)].copy()
        town_options = ["All towns"]
    else:
        governorate_data = df[df["Governorate"] == governorate].copy()
        town_options = ["All towns"] + sorted(governorate_data["Town"].dropna().unique().tolist())

    town = st.selectbox(
        "Town",
        town_options,
        disabled=(governorate == "All Lebanon"),
        help="Town choices are linked to the selected governorate."
    )

if governorate == "All Lebanon":
    profile_data = df
    profile_title = "Average Education Profile Across Lebanese Towns — 2023"
    scope_label = "Lebanon"
elif town == "All towns":
    profile_data = governorate_data
    profile_title = f"Average Education Profile Across Towns in {governorate} — 2023"
    scope_label = governorate
else:
    profile_data = governorate_data[governorate_data["Town"] == town].copy()
    profile_title = f"Education Profile — {town}, {governorate} — 2023"
    scope_label = town

profile = education_profile(profile_data)

scatter_scope = governorate_data
scatter_clean = scatter_scope.dropna(
    subset=["Governorate", "Town", "School_Dropout", "University", "Higher_Education"]
).copy()
scatter_clean["Higher_Education_Attainment"] = scatter_clean["University"] + scatter_clean["Higher_Education"]

kpi_scope = (
    scatter_clean[scatter_clean["Town"] == town].copy()
    if town != "All towns"
    else scatter_clean.copy()
)

town_count = 1 if town != "All towns" and not kpi_scope.empty else int(kpi_scope["Town"].nunique())
avg_dropout = kpi_scope["School_Dropout"].mean() if not kpi_scope.empty else np.nan
avg_higher_ed = kpi_scope["Higher_Education_Attainment"].mean() if not kpi_scope.empty else np.nan

if not profile.empty:
    leading_row = profile.loc[profile["Percentage"].idxmax()]
    leading_level = leading_row["Education_Level"]
    leading_pct = leading_row["Percentage"]
else:
    leading_level, leading_pct = "N/A", np.nan

k1, k2, k3, k4 = st.columns(4)
k1.metric("Towns", f"{town_count:,}")
k2.metric("Avg. School Dropout", "N/A" if pd.isna(avg_dropout) else f"{avg_dropout:.1f}%")
k3.metric("Avg. Higher Education", "N/A" if pd.isna(avg_higher_ed) else f"{avg_higher_ed:.1f}%")
k4.metric(
    "Leading Education Level",
    leading_level,
    delta=None if pd.isna(leading_pct) else f"{leading_pct:.1f}% share",
    delta_color="off"
)

st.subheader(f"Education Profile — {scope_label}")

if not profile.empty:
    st.plotly_chart(
        donut_chart(profile, profile_title),
        use_container_width=True
    )

    with st.expander("💡 Insight"):
        st.markdown(
            """Educational attainment appears relatively evenly distributed across the three largest categories, with **Intermediate (20.2%)**, **University (19.9%)**, and **Secondary (19.2%)** showing very similar shares. This suggests that no single education level dominates the national town-level profile. Filtering by governorate or town provides further insight into disparities across locations."""
        )
else:
    st.warning("There are not enough complete education-level values for this selection.")

st.divider()
st.subheader("School Dropout vs. Higher Education Attainment")

fig_scatter, scatter_used = scatter_chart(scatter_scope, town)
st.plotly_chart(fig_scatter, use_container_width=True)

with st.expander("💡 Insight"):
    st.markdown(
        """The relationship between higher education attainment and school dropout appears relatively weak overall. However, towns with very high dropout rates tend to be concentrated at lower levels of higher education attainment. This suggests that educational attainment alone does not explain differences in school dropout across towns. Filtering by governorate allows the relationship and variation within individual regions to be examined more closely."""
    )

st.divider()

with st.expander("Interaction design"):
    st.markdown("""
**Governorate selector.** This dropdown helps users visualize and compare education and dropout patterns across governorates. A dropdown was chosen because the user can focus on one governorate at a time instead of viewing all locations together. This reduces clutter and makes geographic differences easier to explore.

**Town selector.** This dropdown allows users to explore education and dropout patterns at the town level within the selected governorate. The available towns change based on the governorate selected, creating a linked interaction that allows users to drill down from governorate to town. A dropdown was chosen instead of a multiselect because the focus is on exploring one town at a time, which reduces clutter and makes local differences easier to identify.

**Education level selection.** Users can click the education levels in the donut chart legend to hide or display individual categories. Multiple levels can be removed or displayed at the same time, allowing users to focus on specific education levels and make the chart less cluttered.
""")

with st.expander("About the data"):
    st.markdown("""
**Source:** LinkedAUB PKGCube Explorer, 2023.

The dataset reports education-level percentages and school-dropout rates at the town/locality level. Beirut is not represented in the source dataset. Towns were grouped into their respective governorates to support geographic comparisons.

Values outside the valid 0–100% range were treated as missing. Education profiles are calculated using observations with complete data across all seven education levels. Lebanon and governorate figures represent **averages across towns and are not population-weighted**.

For this analysis, **Higher Education Attainment** is defined as the combined percentage of **University + Higher Education**.
""")
