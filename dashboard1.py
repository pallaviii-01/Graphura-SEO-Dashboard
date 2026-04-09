"""
Graphura India — SEO Opportunity Dashboard
Streamlit + Plotly Interactive Dashboard

Run with:
    pip install streamlit plotly pandas openpyxl
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Graphura SEO Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME / CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #F8FAFC; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #002366 0%, #1565C0 100%); }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { color: #BBDEFB !important; font-size: 0.85rem; }

    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 5px solid #1565C0;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .kpi-card .kpi-value { font-size: 2rem; font-weight: 800; color: #002366; margin: 0; }
    .kpi-card .kpi-label { font-size: 0.75rem; color: #607D8B; margin: 0; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-card.green  { border-left-color: #1B5E20; }
    .kpi-card.green  .kpi-value { color: #1B5E20; }
    .kpi-card.orange { border-left-color: #E65100; }
    .kpi-card.orange .kpi-value { color: #E65100; }
    .kpi-card.red    { border-left-color: #B71C1C; }
    .kpi-card.red    .kpi-value { color: #B71C1C; }
    .kpi-card.purple { border-left-color: #4A148C; }
    .kpi-card.purple .kpi-value { color: #4A148C; }
    .kpi-card.teal   { border-left-color: #006064; }
    .kpi-card.teal   .kpi-value { color: #006064; }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #1565C0, #1E88E5);
        color: white !important;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.8rem;
        margin-top: 0.5rem;
    }

    /* Page title */
    .main-title {
        background: linear-gradient(135deg, #002366 0%, #1565C0 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .main-title h1 { color: white; margin: 0; font-size: 1.9rem; }
    .main-title p  { color: #BBDEFB; margin: 0.3rem 0 0; font-size: 0.9rem; }

    /* Dataframe styling */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
    }

    /* Hide streamlit default header */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    master = pd.read_excel("Graphura_SEO_Master_Dataset_Final.xlsx", sheet_name="Master SEO Dataset")
    gap = pd.read_excel("Graphura_Competitor_SEO_Analysis.xlsx", sheet_name="Content Gap Analysis", header=1)

    # ✅ FIX: CLEAN COLUMNS
    master.columns = master.columns.str.strip()
    gap.columns = gap.columns.str.strip()

    gap = gap.iloc[1:].reset_index(drop=True)

    gap.columns = [
        "Keyword", "Keyword_Category", "Search_Volume", "Keyword_Difficulty",
        "Opportunity_Score", "Graphura_Ranking", "Best_Competitor_Rank",
        "Ranking_Gap", "Competitors_Ahead", "No_Competitors_Ahead",
        "Gap_Priority_Score", "Recommended_Content", "Action_Required"
    ]

    for col in ["Search_Volume", "Opportunity_Score", "Gap_Priority_Score",
                "No_Competitors_Ahead", "Graphura_Ranking", "Keyword_Difficulty",
                "Best_Competitor_Rank", "Ranking_Gap"]:
        gap[col] = pd.to_numeric(gap[col], errors="coerce")

    roadmap = pd.read_excel("Graphura_Competitor_SEO_Analysis.xlsx", sheet_name="SEO Roadmap", header=0)
    roadmap.columns = roadmap.columns.str.strip()
    roadmap = roadmap.iloc[1:].reset_index(drop=True)

    roadmap.columns = [
        "Priority_Rank", "Month", "Keyword", "Keyword_Category",
        "Search_Volume", "Graphura_Ranking", "Gap_Priority_Score",
        "Content_to_Create", "Action", "Target_Ranking", "Effort_Level"
    ]

    for col in ["Priority_Rank", "Search_Volume", "Graphura_Ranking", "Gap_Priority_Score"]:
        roadmap[col] = pd.to_numeric(roadmap[col], errors="coerce")

    return master, gap, roadmap



# ─────────────────────────────────────────────────────────────────────────────
# HELPER: KPI card HTML
# ─────────────────────────────────────────────────────────────────────────────
def kpi_card(label, value, color="blue", delta=None):
    delta_html = f"<div style='font-size:0.72rem;color:#78909C;margin-top:0.2rem'>{delta}</div>" if delta else ""
    return f"""
    <div class="kpi-card {color}">
        <p class="kpi-label">{label}</p>
        <p class="kpi-value">{value}</p>
        {delta_html}
    </div>
    """

# ─────────────────────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────────────────────
try:
    df, df_gap, df_road = load_data()
except FileNotFoundError:
    st.error("""
    ⚠️ **Data files not found!**

    Please place these files in the same folder as `app.py`:
    - `Graphura_SEO_Master_Dataset_Final.xlsx`
    - `Graphura_Competitor_SEO_Analysis.xlsx`

    Then run: `streamlit run app.py`
    """)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    priority_opts = ["All"] + sorted(df["Priority"].unique().tolist())
    selected_priority = st.selectbox("Priority Level", priority_opts)

    category_opts = ["All"] + sorted(df["Keyword Category"].unique().tolist())
    selected_category = st.selectbox("Keyword Category", category_opts)

    intent_opts = ["All"] + sorted(df["Search Intent"].unique().tolist())
    selected_intent = st.selectbox("Search Intent", intent_opts)

    min_vol, max_vol = int(df["Search Volume"].min()), int(df["Search Volume"].max())
    vol_range = st.slider("Search Volume Range", min_vol, max_vol, (min_vol, max_vol), step=100)

    min_opp = st.slider("Min Opportunity Score", 0, int(df["Opportunity Score"].max()), 0)

    st.markdown("---")
    st.markdown("### 📌 About")
    st.markdown("""
    **Graphura India SEO Dashboard**    
    April 2026

    Data: 714 Keywords  
    Competitors: 5 agencies  
    """)

# ─────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
dff = df.copy()
if selected_priority != "All":
    dff = dff[dff["Priority"] == selected_priority]
if selected_category != "All":
    dff = dff[dff["Keyword Category"] == selected_category]
if selected_intent != "All":
    dff = dff[dff["Search Intent"] == selected_intent]
dff = dff[(dff["Search Volume"] >= vol_range[0]) & (dff["Search Volume"] <= vol_range[1])]
dff = dff[dff["Opportunity Score"] >= min_opp]

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-title">
    <h1>📊 Graphura India — SEO Opportunity Dashboard</h1>
    <p>Step 3 & Step 4 | Keyword Performance, Content Gap Analysis & 3-Month SEO Roadmap | April 2026</p>
</div>
""", unsafe_allow_html=True)

# Active filter badge
active_filters = sum([
    selected_priority != "All",
    selected_category != "All",
    selected_intent != "All",
    vol_range != (min_vol, max_vol),
    min_opp > 0
])
if active_filters:
    st.info(f"🔽 **{active_filters} filter(s) active** — showing {len(dff)} of {len(df)} keywords")

# ─────────────────────────────────────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

high_cnt  = (dff["Priority"] == "High").sum()
med_cnt   = (dff["Priority"] == "Medium").sum()
low_cnt   = (dff["Priority"] == "Low").sum()
avg_opp   = dff["Opportunity Score"].mean()
total_vol = dff["Search Volume"].sum()

with k1:
    st.markdown(kpi_card("Total Keywords", f"{len(dff):,}", "blue",
                         f"of {len(df):,} total"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("High Priority", f"{high_cnt:,}", "green",
                         f"{high_cnt/max(len(dff),1)*100:.0f}% of filtered"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Medium Priority", f"{med_cnt:,}", "orange",
                         f"{med_cnt/max(len(dff),1)*100:.0f}% of filtered"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card("Low Priority", f"{low_cnt:,}", "red",
                         f"{low_cnt/max(len(dff),1)*100:.0f}% of filtered"), unsafe_allow_html=True)
with k5:
    st.markdown(kpi_card("Avg Opp Score", f"{avg_opp:.0f}", "purple",
                         "Higher = better opportunity"), unsafe_allow_html=True)
with k6:
    st.markdown(kpi_card("Total Search Vol", f"{total_vol:,.0f}", "teal",
                         "Monthly searches"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Keyword Analysis",
    "🔍 Content Gap",
    "🗺️ SEO Roadmap",
    "📊 Category Insights",
    "🤖 ML Labels",
    "🔥 Priority Keywords"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — KEYWORD ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1])

    # Priority Donut Chart
    with col_left:
        st.markdown('<div class="section-header">▌ Priority Distribution</div>', unsafe_allow_html=True)
        priority_counts = dff["Priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Count"]
        colors_p = {"High": "#1B5E20", "Medium": "#E65100", "Low": "#B71C1C"}
        fig_donut = px.pie(
            priority_counts, names="Priority", values="Count",
            hole=0.55,
            color="Priority",
            color_discrete_map=colors_p,
        )
        fig_donut.update_traces(textinfo="percent+label", textfont_size=13,
                                marker=dict(line=dict(color="white", width=2)))
        fig_donut.update_layout(
            showlegend=True, height=320,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # Search Intent Bar
    with col_right:
        st.markdown('<div class="section-header">▌ Search Intent Mix</div>', unsafe_allow_html=True)
        intent_counts = dff["Search Intent"].value_counts().reset_index()
        intent_counts.columns = ["Intent", "Count"]
        intent_colors = {"Commercial": "#1565C0", "Transactional": "#1B5E20", "Informational": "#6A1B9A"}
        fig_intent = px.bar(
            intent_counts, x="Intent", y="Count",
            color="Intent", color_discrete_map=intent_colors,
            text="Count",
        )
        fig_intent.update_traces(textposition="outside", textfont_size=13)
        fig_intent.update_layout(
            height=320, showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title="", yaxis_title="Keyword Count",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#ECEFF1"),
        )
        st.plotly_chart(fig_intent, use_container_width=True)

    st.markdown("---")

    # Scatter: Search Volume vs Opportunity Score
    st.markdown('<div class="section-header">▌ Search Volume vs Opportunity Score — Bubble Chart</div>', unsafe_allow_html=True)
    top_scatter = dff.nlargest(200, "Opportunity Score")  # limit for performance
    color_map_s = {"High": "#1B5E20", "Medium": "#F9A825", "Low": "#B71C1C"}
    fig_scatter = px.scatter(
        top_scatter,
        x="Search Volume", y="Opportunity Score",
        color="Priority", size="Relevance(0-100)",
        hover_name="Keyword",
        hover_data={"Keyword Category": True, "Keyword Difficulty": True,
                    "Graphura Current Ranking": True, "Priority": False},
        color_discrete_map=color_map_s,
        size_max=20,
        labels={"Search Volume": "Monthly Search Volume", "Opportunity Score": "Opportunity Score"},
    )
    fig_scatter.update_layout(
        height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#ECEFF1", zeroline=False),
        yaxis=dict(gridcolor="#ECEFF1", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=30, b=20),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # Top Keywords Table
    st.markdown('<div class="section-header">▌ Top 25 Keywords by Opportunity Score</div>', unsafe_allow_html=True)
    top25 = dff.nlargest(25, "Opportunity Score")[
        ["Keyword", "Keyword Category", "Search Volume", "Keyword Difficulty",
         "Graphura Current Ranking", "Opportunity Score", "Priority", "Search Intent"]
    ].reset_index(drop=True)
    top25.index += 1

   def highlight_priority(val):
     colors = {
        "High": "background-color:#E8F5E9;color:#1B5E20;font-weight:bold",
        "Medium": "background-color:#FFFDE7;color:#E65100;font-weight:bold",
        "Low": "background-color:#FFEBEE;color:#B71C1C;font-weight:bold"
    }
     return colors.get(val, "")


   styled = top25.style.map(highlight_priority, subset=["Priority"])
    st.write(styled)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CONTENT GAP
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">▌ Content Gap Overview — Where Competitors Win But Graphura Doesn\'t</div>',
                unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)
    lp = (df_gap["Recommended_Content"] == "Landing Page").sum()
    sp = (df_gap["Recommended_Content"] == "Service Page").sum()
    bp = (df_gap["Recommended_Content"] == "Blog Post").sum()
    top20_vol = df_gap.nlargest(20, "Gap_Priority_Score")["Search_Volume"].sum()

    with g1:
        st.markdown(kpi_card("Total Gap Keywords", "88", "red", "Act on these first"), unsafe_allow_html=True)
    with g2:
        st.markdown(kpi_card("Landing Pages Needed", str(lp), "orange", "Highest impact"), unsafe_allow_html=True)
    with g3:
        st.markdown(kpi_card("Service Pages Needed", str(sp), "teal", "Category authority"), unsafe_allow_html=True)
    with g4:
        st.markdown(kpi_card("Blog Posts Needed", str(bp), "green", "Informational intent"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    gc1, gc2 = st.columns([1, 1])

    with gc1:
        # Content type distribution
        st.markdown('<div class="section-header">▌ Recommended Content Type Distribution</div>', unsafe_allow_html=True)
        ct_counts = df_gap["Recommended_Content"].value_counts().reset_index()
        ct_counts.columns = ["Content Type", "Count"]
        fig_ct = px.bar(ct_counts, x="Content Type", y="Count", text="Count",
                       color="Content Type",
                       color_discrete_sequence=["#1565C0", "#1B5E20", "#E65100"])
        fig_ct.update_traces(textposition="outside")
        fig_ct.update_layout(height=320, showlegend=False, margin=dict(t=20,b=10,l=10,r=10),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            yaxis=dict(gridcolor="#ECEFF1"), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_ct, use_container_width=True)

    with gc2:
        # Action required distribution
        st.markdown('<div class="section-header">▌ Action Required</div>', unsafe_allow_html=True)
        act_counts = df_gap["Action_Required"].value_counts().reset_index()
        act_counts.columns = ["Action", "Count"]
        fig_act = px.pie(act_counts, names="Action", values="Count",
                        hole=0.5,
                        color_discrete_sequence=["#1565C0", "#E65100"])
        fig_act.update_traces(textinfo="percent+label", textfont_size=12,
                             marker=dict(line=dict(color="white", width=2)))
        fig_act.update_layout(height=320, margin=dict(t=20,b=10,l=10,r=10),
                             paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_act, use_container_width=True)

    st.markdown("---")

    # Top 20 Gap Keywords Horizontal Bar
    st.markdown('<div class="section-header">▌ Top 20 Content Gap Keywords by Gap Priority Score</div>',
                unsafe_allow_html=True)
    top20_gap = df_gap.nlargest(20, "Gap_Priority_Score").copy()
    top20_gap["Keyword_Short"] = top20_gap["Keyword"].str[:45]
    fig_gap_bar = px.bar(
        top20_gap.sort_values("Gap_Priority_Score"),
        x="Gap_Priority_Score", y="Keyword_Short",
        orientation="h", color="Gap_Priority_Score",
        color_continuous_scale=["#FFF9C4", "#F9A825", "#B71C1C"],
        hover_data={"Search_Volume": True, "Graphura_Ranking": True,
                    "Best_Competitor_Rank": True, "Recommended_Content": True},
        labels={"Gap_Priority_Score": "Gap Priority Score", "Keyword_Short": ""},
    )
    fig_gap_bar.update_layout(
        height=550, margin=dict(t=10,b=10,l=10,r=80),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#ECEFF1"), coloraxis_showscale=False,
        yaxis=dict(tickfont=dict(size=11)),
    )
    st.plotly_chart(fig_gap_bar, use_container_width=True)

    st.markdown("---")

    # Competitor Ranking Gap Heatmap
    st.markdown('<div class="section-header">▌ Competitor Coverage Heatmap — Avg SERP Rank by Category</div>',
                unsafe_allow_html=True)

    heatmap_data = {
        "Keyword Category": ["Digital Mktg Agency","PPC / Paid Ads","SEO Services",
                             "Social Media Mktg","Content Marketing","Branding","Growth Marketing"],
        "Graphura":  [52.2, 59.8, 56.3, 59.0, 48.3, 47.6, 37.2],
        "Social Beat":[4.1,  13.0,  4.0, 4.1,  5.3, 12.0, 50.0],
        "WatConsult": [4.6,   4.0, 11.3, 4.5, 11.0,  6.0, 50.0],
        "iProspect":  [4.3,   4.9,  4.3,12.2,  9.0, 13.0, 50.0],
        "Webchutney": [4.3,  11.0, 14.2, 5.0,  3.7,  1.0, 50.0],
        "Mirum India":[4.9,  12.4, 14.5,12.2,  3.0,  1.0, 50.0],
    }
    df_heat = pd.DataFrame(heatmap_data).set_index("Keyword Category")

    fig_heat = go.Figure(data=go.Heatmap(
        z=df_heat.values,
        x=df_heat.columns.tolist(),
        y=df_heat.index.tolist(),
        colorscale=[[0,"#1B5E20"],[0.2,"#4CAF50"],[0.4,"#FFF9C4"],
                    [0.6,"#F9A825"],[0.8,"#EF5350"],[1,"#B71C1C"]],
        text=df_heat.values,
        texttemplate="%{text}",
        textfont={"size": 12, "color": "white"},
        hovertemplate="<b>%{y}</b><br>%{x}: Avg Rank %{z}<extra></extra>",
        showscale=True,
        colorbar=dict(title="Avg Rank", tickfont=dict(size=11)),
    ))
    fig_heat.update_layout(
        height=400,
        margin=dict(t=20,b=20,l=10,r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(side="top", tickfont=dict(size=12, color="#002366")),
        yaxis=dict(tickfont=dict(size=11)),
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("🟢 Lower rank = better (1 = #1 on Google) | 🔴 Graphura is 40–56 positions behind all competitors in core categories")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SEO ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">▌ 3-Month SEO Content Roadmap — Step 4 Deliverable</div>',
                unsafe_allow_html=True)

    rc1, rc2, rc3 = st.columns(3)
    m1 = df_road[df_road["Month"] == "Month 1"]
    m2 = df_road[df_road["Month"] == "Month 2"]
    m3 = df_road[df_road["Month"] == "Month 3"]

    with rc1:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1A237E,#3949AB);color:white;
                    border-radius:10px;padding:1rem;text-align:center'>
            <div style='font-size:1.8rem;font-weight:800'>{}</div>
            <div style='font-size:0.85rem;opacity:0.85'>📅 Month 1 — Quick Wins</div>
            <div style='font-size:0.75rem;opacity:0.7;margin-top:0.3rem'>Optimise existing pages</div>
        </div>
        """.format(len(m1)), unsafe_allow_html=True)

    with rc2:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1B5E20,#388E3C);color:white;
                    border-radius:10px;padding:1rem;text-align:center'>
            <div style='font-size:1.8rem;font-weight:800'>{}</div>
            <div style='font-size:0.85rem;opacity:0.85'>📅 Month 2 — Growth Phase</div>
            <div style='font-size:0.75rem;opacity:0.7;margin-top:0.3rem'>Create new content</div>
        </div>
        """.format(len(m2)), unsafe_allow_html=True)

    with rc3:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#4A148C,#7B1FA2);color:white;
                    border-radius:10px;padding:1rem;text-align:center'>
            <div style='font-size:1.8rem;font-weight:800'>{}</div>
            <div style='font-size:0.85rem;opacity:0.85'>📅 Month 3 — Authority Build</div>
            <div style='font-size:0.75rem;opacity:0.7;margin-top:0.3rem'>Transactional + long-tail</div>
        </div>
        """.format(len(m3)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Roadmap Gantt-style timeline
    st.markdown('<div class="section-header">▌ Roadmap Timeline — Gap Priority Score by Month</div>',
                unsafe_allow_html=True)
    road_chart = df_road.copy()
    road_chart["Keyword_Short"] = road_chart["Keyword"].str[:40]
    month_colors = {"Month 1": "#1A237E", "Month 2": "#1B5E20", "Month 3": "#4A148C"}
    fig_road = px.bar(
        road_chart.sort_values(["Month","Gap_Priority_Score"], ascending=[True,False]).head(30),
        x="Gap_Priority_Score", y="Keyword_Short",
        color="Month", orientation="h",
        color_discrete_map=month_colors,
        hover_data={"Content_to_Create": True, "Effort_Level": True,
                    "Target_Ranking": True, "Action": True},
        labels={"Gap_Priority_Score": "Gap Priority Score", "Keyword_Short": ""},
        barmode="overlay",
    )
    fig_road.update_layout(
        height=600, margin=dict(t=10,b=10,l=10,r=50),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#ECEFF1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_road, use_container_width=True)

    st.markdown("---")

    # Effort distribution
    re1, re2 = st.columns([1, 1])
    with re1:
        st.markdown('<div class="section-header">▌ Effort Level Distribution</div>', unsafe_allow_html=True)
        effort_c = df_road["Effort_Level"].value_counts().reset_index()
        effort_c.columns = ["Effort", "Count"]
        effort_clr = {"Low": "#1B5E20", "Medium": "#F9A825", "High": "#B71C1C"}
        fig_effort = px.bar(effort_c, x="Effort", y="Count", text="Count",
                           color="Effort", color_discrete_map=effort_clr)
        fig_effort.update_traces(textposition="outside")
        fig_effort.update_layout(height=280, showlegend=False, margin=dict(t=10,b=10,l=10,r=10),
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                yaxis=dict(gridcolor="#ECEFF1"), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_effort, use_container_width=True)

    with re2:
        st.markdown('<div class="section-header">▌ Content Type by Month</div>', unsafe_allow_html=True)
        ct_month = df_road.groupby(["Month","Content_to_Create"]).size().reset_index(name="Count")
        fig_ct_m = px.bar(ct_month, x="Month", y="Count", color="Content_to_Create",
                         color_discrete_sequence=["#1565C0","#1B5E20","#E65100"],
                         barmode="group", text="Count")
        fig_ct_m.update_traces(textposition="outside")
        fig_ct_m.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               yaxis=dict(gridcolor="#ECEFF1"), xaxis_title="", yaxis_title="",
                               legend=dict(title="Content Type", font=dict(size=10)))
        st.plotly_chart(fig_ct_m, use_container_width=True)

    st.markdown("---")

    # Full Roadmap Table
    st.markdown('<div class="section-header">▌ Full Roadmap Table</div>', unsafe_allow_html=True)
    month_filter = st.selectbox("Filter by Month", ["All", "Month 1", "Month 2", "Month 3"])
    road_disp = df_road if month_filter == "All" else df_road[df_road["Month"] == month_filter]
    road_disp = road_disp[["Priority_Rank","Month","Keyword","Keyword_Category",
                            "Search_Volume","Gap_Priority_Score","Content_to_Create",
                            "Action","Target_Ranking","Effort_Level"]].copy()
    road_disp.columns = ["#","Month","Keyword","Category","Search Vol",
                         "Gap Score","Content Type","Action","Target Rank","Effort"]

    def color_effort(val):
    m = {
        "Low": "background-color:#E8F5E9;color:#1B5E20",
        "Medium": "background-color:#FFFDE7;color:#E65100",
        "High": "background-color:#FFEBEE;color:#B71C1C"
    }
    return m.get(val, "")

def color_month(val):
    m = {
        "Month 1": "background-color:#E8EAF6;color:#1A237E;font-weight:bold",
        "Month 2": "background-color:#E8F5E9;color:#1B5E20;font-weight:bold",
        "Month 3": "background-color:#F3E5F5;color:#4A148C;font-weight:bold"
    }
    return m.get(val, "")



styled_road = road_disp.style \
    .map(color_effort, subset=["Effort"]) \
    .map(color_month, subset=["Month"])

st.write(styled_road)
# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CATEGORY INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">▌ Keyword Category Deep-Dive</div>', unsafe_allow_html=True)

    cat_agg = dff.groupby("Keyword Category").agg(
        Total=("Keyword","count"),
        High=("Priority", lambda x: (x=="High").sum()),
        Medium=("Priority", lambda x: (x=="Medium").sum()),
        Low=("Priority", lambda x: (x=="Low").sum()),
        Avg_Vol=("Search Volume","mean"),
        Avg_Diff=("Keyword Difficulty","mean"),
        Avg_Opp=("Opportunity Score","mean"),
        Max_Opp=("Opportunity Score","max"),
        Total_Vol=("Search Volume","sum"),
    ).round(1).reset_index().sort_values("High", ascending=False)

    ci1, ci2 = st.columns([1, 1])

    with ci1:
        # Stacked bar: priority by category
        st.markdown('<div class="section-header">▌ Priority Distribution by Category</div>', unsafe_allow_html=True)
        cat_melt = cat_agg.melt(id_vars="Keyword Category", value_vars=["High","Medium","Low"],
                                var_name="Priority", value_name="Count")
        p_colors = {"High":"#1B5E20","Medium":"#F9A825","Low":"#B71C1C"}
        fig_stacked = px.bar(cat_melt, x="Keyword Category", y="Count",
                            color="Priority", color_discrete_map=p_colors,
                            barmode="stack")
        fig_stacked.update_layout(
            height=380, margin=dict(t=10,b=90,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickangle=-30, gridcolor="#ECEFF1"),
            yaxis=dict(gridcolor="#ECEFF1"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_title="", yaxis_title="Keywords",
        )
        st.plotly_chart(fig_stacked, use_container_width=True)

    with ci2:
        # Treemap: category by total search vol
        st.markdown('<div class="section-header">▌ Total Search Volume by Category (Treemap)</div>',
                    unsafe_allow_html=True)
        fig_tree = px.treemap(
            cat_agg, path=["Keyword Category"], values="Total_Vol",
            color="Avg_Opp",
            color_continuous_scale=["#BBDEFB","#1565C0","#002366"],
            hover_data={"Total":True,"High":True,"Avg_Opp":True},
        )
        fig_tree.update_layout(
            height=380, margin=dict(t=10,b=10,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(title="Avg Opp Score"),
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")

    ci3, ci4 = st.columns([1, 1])

    with ci3:
        # Avg Opportunity Score by Category
        st.markdown('<div class="section-header">▌ Avg Opportunity Score by Category</div>',
                    unsafe_allow_html=True)
        cat_sorted = cat_agg.sort_values("Avg_Opp", ascending=True)
        fig_opp = px.bar(cat_sorted, x="Avg_Opp", y="Keyword Category",
                        orientation="h", text="Avg_Opp",
                        color="Avg_Opp",
                        color_continuous_scale=["#E3F2FD","#1565C0","#002366"])
        fig_opp.update_traces(textposition="outside")
        fig_opp.update_layout(
            height=350, margin=dict(t=10,b=10,l=10,r=60),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#ECEFF1"), yaxis_title="", xaxis_title="Avg Opportunity Score",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_opp, use_container_width=True)

    with ci4:
        # Scatter: Avg Difficulty vs Avg Opportunity
        st.markdown('<div class="section-header">▌ Difficulty vs Opportunity by Category</div>',
                    unsafe_allow_html=True)
        fig_dv = px.scatter(
            cat_agg, x="Avg_Diff", y="Avg_Opp",
            size="Total", color="Keyword Category",
            hover_name="Keyword Category",
            text="Keyword Category",
            size_max=35,
        )
        fig_dv.update_traces(textposition="top center", textfont_size=9)
        fig_dv.update_layout(
            height=350, margin=dict(t=10,b=10,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Avg Keyword Difficulty", gridcolor="#ECEFF1"),
            yaxis=dict(title="Avg Opportunity Score", gridcolor="#ECEFF1"),
            showlegend=False,
        )
        # Quadrant annotations
        fig_dv.add_annotation(x=20, y=cat_agg["Avg_Opp"].max()*0.9,
            text="🎯 Quick Wins", showarrow=False,
            font=dict(color="#1B5E20", size=10))
        fig_dv.add_annotation(x=50, y=cat_agg["Avg_Opp"].max()*0.9,
            text="⚠️ Hard & Valuable", showarrow=False,
            font=dict(color="#E65100", size=10))
        st.plotly_chart(fig_dv, use_container_width=True)

    st.markdown("---")

    # Category Summary Table
    st.markdown('<div class="section-header">▌ Category Summary Table</div>', unsafe_allow_html=True)
    cat_display = cat_agg.copy()
    cat_display.columns = ["Category","Total","High","Medium","Low",
                           "Avg Search Vol","Avg Difficulty","Avg Opp Score",
                           "Max Opp Score","Total Search Vol"]
    cat_display["% High"] = (cat_display["High"]/cat_display["Total"]*100).round(0).astype(int).astype(str)+"%"
    st.dataframe(cat_display, use_container_width=True, height=350)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ML LABELS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">▌ ML Opportunity Label Analysis — Model Prep (Steps 5–8)</div>',
                unsafe_allow_html=True)

    ml_map = {2: "High (2)", 1: "Medium (1)", 0: "Low (0)"}
    dff["ML Label Name"] = dff["ML Label"].map(ml_map)

    ml1, ml2 = st.columns([1, 1])

    with ml1:
        # ML label distribution
        ml_counts = dff["ML Label Name"].value_counts().reset_index()
        ml_counts.columns = ["ML Label", "Count"]
        ml_colors_map = {"High (2)": "#1B5E20", "Medium (1)": "#F9A825", "Low (0)": "#B71C1C"}
        fig_ml = px.pie(ml_counts, names="ML Label", values="Count", hole=0.55,
                       color="ML Label", color_discrete_map=ml_colors_map)
        fig_ml.update_traces(textinfo="percent+label", textfont_size=13,
                            marker=dict(line=dict(color="white", width=2)))
        fig_ml.update_layout(height=340, paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=20,b=10,l=10,r=10))
        st.plotly_chart(fig_ml, use_container_width=True)

    with ml2:
        # Feature comparison: Opp Score by ML Label
        ml_agg = dff.groupby("ML Label Name").agg(
            Avg_Vol=("Search Volume","mean"),
            Avg_Diff=("Keyword Difficulty","mean"),
            Avg_Opp=("Opportunity Score","mean"),
            Avg_Rank=("Graphura Current Ranking","mean"),
            Count=("Keyword","count"),
        ).round(1).reset_index()

        fig_ml_feat = go.Figure()
        features = ["Avg_Vol","Avg_Diff","Avg_Opp","Avg_Rank"]
        feat_labels = ["Avg Search Vol","Avg KW Diff","Avg Opp Score","Avg Curr Rank"]
        ml_order = ["High (2)","Medium (1)","Low (0)"]
        ml_colors_lst = ["#1B5E20","#F9A825","#B71C1C"]

        for label,clr in zip(ml_order, ml_colors_lst):
            row = ml_agg[ml_agg["ML Label Name"]==label]
            if len(row)==0: continue
            vals = [row[f].values[0] for f in features]
            # Normalize for radar
            fig_ml_feat.add_trace(go.Bar(
                name=label,
                x=feat_labels,
                y=vals,
                marker_color=clr,
                text=[f"{v:.0f}" for v in vals],
                textposition="outside",
            ))
        fig_ml_feat.update_layout(
            height=340, barmode="group",
            margin=dict(t=10,b=10,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#ECEFF1"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_ml_feat, use_container_width=True)

    st.markdown("---")

    # Box plots: Opportunity Score distribution by ML Label
    st.markdown('<div class="section-header">▌ Opportunity Score Distribution by ML Label</div>',
                unsafe_allow_html=True)
    fig_box = px.box(
        dff, x="ML Label Name", y="Opportunity Score",
        color="ML Label Name", color_discrete_map=ml_colors_map,
        points="outliers",
        category_orders={"ML Label Name": ["High (2)","Medium (1)","Low (0)"]},
    )
    fig_box.update_layout(
        height=340, showlegend=False,
        margin=dict(t=10,b=10,l=10,r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="ML Label", yaxis_title="Opportunity Score",
        yaxis=dict(gridcolor="#ECEFF1"),
    )
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # Model Feature Summary Table
    st.markdown('<div class="section-header">▌ Feature Pattern Summary per ML Label</div>',
                unsafe_allow_html=True)
    ml_full = dff.groupby("ML Label Name").agg(
        Count=("Keyword","count"),
        Avg_Search_Vol=("Search Volume","mean"),
        Avg_KW_Difficulty=("Keyword Difficulty","mean"),
        Avg_Current_Rank=("Graphura Current Ranking","mean"),
        Avg_Opportunity_Score=("Opportunity Score","mean"),
        Avg_Relevance=("Relevance(0-100)","mean"),
        Top_Intent=("Search Intent", lambda x: x.mode()[0]),
    ).round(1).reset_index()
    ml_full.columns = ["ML Label","Count","Avg Search Vol","Avg KW Difficulty",
                       "Avg Current Rank","Avg Opp Score","Avg Relevance","Top Intent"]
    st.dataframe(ml_full, use_container_width=True)

    st.markdown("""
    > **💡 ML Model Notes for Steps 5–8:**
    > - **Features to use:** Search Volume, KW Difficulty, Current Ranking, Competition, Relevance, Search Intent (encoded), Competitor Presence (encoded)
    > - **Target:** ML Label (0/1/2) — multiclass classification
    > - **Suggested Models:** Random Forest, XGBoost, LightGBM (try all, compare F1 score)
    > - **Class imbalance:** Medium (398) >> High (216) > Low (100) — use SMOTE or class weights
    > - **Train/Test split:** 80/20 stratified by ML Label
    """)



    # ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — PRIORITY KEYWORDS (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">▌ High Priority & Top Keywords Strategy</div>', unsafe_allow_html=True)

    # Split columns
    pk1, pk2 = st.columns([1,1])

    # ─────────────────────────────────────────
    # HIGH PRIORITY KEYWORDS
    # ─────────────────────────────────────────
    with pk1:
        st.markdown("### 🔥 High Priority Keywords (Immediate Focus)")

        high_df = dff[dff["Priority"] == "High"] \
            .sort_values("Opportunity Score", ascending=False) \
            .head(20)

        high_df = high_df[[
            "Keyword", "Keyword Category", "Search Volume",
            "Keyword Difficulty", "Opportunity Score",
            "Graphura Current Ranking"
        ]]

        st.dataframe(high_df, use_container_width=True, height=400)

        st.success("""
        💡 **Strategy:**
        - Target these keywords FIRST
        - High traffic + High opportunity
        - Quick ranking improvement possible
        """)

    # ─────────────────────────────────────────
    # TOP KEYWORDS (OVERALL BEST)
    # ─────────────────────────────────────────
    with pk2:
        st.markdown("### 🚀 Top Keywords (Best Overall Opportunities)")

        top_df = dff.sort_values(
            ["Opportunity Score", "Search Volume"],
            ascending=[False, False]
        ).head(20)

        top_df = top_df[[
            "Keyword", "Priority", "Search Volume",
            "Opportunity Score", "Keyword Difficulty"
        ]]

        st.dataframe(top_df, use_container_width=True, height=400)

        st.info("""
        📊 **Insight:**
        - Combination of high volume + high opportunity
        - Ideal for long-term SEO growth
        """)

    st.markdown("---")

    # ─────────────────────────────────────────
    # VISUAL COMPARISON
    # ─────────────────────────────────────────
    st.markdown('<div class="section-header">▌ High vs Top Keywords Comparison</div>', unsafe_allow_html=True)

    comp_df = pd.concat([
        high_df.assign(Type="High Priority"),
        top_df.assign(Type="Top Keywords")
    ])

    fig_compare = px.bar(
        comp_df,
        x="Keyword",
        y="Opportunity Score",
        color="Type",
        barmode="group",
        height=450
    )

    fig_compare.update_layout(
        xaxis_tickangle=-45,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#ECEFF1")
    )

    st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown("---")

    # ─────────────────────────────────────────
    # DOWNLOAD SECTION
    # ─────────────────────────────────────────
    st.markdown("### ⬇️ Download Keyword Lists")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.download_button(
            "📥 Download High Priority Keywords",
            high_df.to_csv(index=False),
            file_name="high_priority_keywords.csv",
            mime="text/csv"
        )

    with col_d2:
        st.download_button(
            "📥 Download Top Keywords",
            top_df.to_csv(index=False),
            file_name="top_keywords.csv",
            mime="text/csv"
        )

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#90A4AE;font-size:0.8rem;padding:1rem'>
     Graphura India SEO Opportunity Dashboard  |  April 2026<br>
    Data: 714 Keywords | 5 Competitors | Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
