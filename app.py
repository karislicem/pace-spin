import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Batter Outperformance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');
    
    /* Global reset & dark theme */
    .stApp {
        background-color: #0a0a0a;
        color: #e5e5e5;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #e5e5e5;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Title styling */
    h1 {
        font-weight: 700;
        font-size: 2.75rem !important;
        letter-spacing: -0.03em;
        margin-bottom: 0.75rem !important;
        color: #ffffff !important;
    }
    
    /* Subtitle/caption */
    .stCaption, p {
        font-size: 0.95rem;
        color: #a3a3a3 !important;
        margin-bottom: 2rem;
    }
    
    /* Subheaders */
    h2, h3 {
        color: #fafafa !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }
    
    /* Sidebar dark theme */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #262626;
    }
    
    section[data-testid="stSidebar"] h2 {
        color: #fafafa;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 1.5rem;
    }
    
    section[data-testid="stSidebar"] label {
        color: #d4d4d4 !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #3b82f6 !important;
        border: none;
    }
    
    /* Slider styling */
    .stSlider {
        padding-top: 1rem;
    }
    
    .stSlider > label {
        font-weight: 500;
        color: #d4d4d4;
        font-size: 0.875rem;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a3a3a3;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Custom metric cards in sidebar */
    .metric-card {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #262626;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #737373;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #0a0a0a;
    }
    
    .dataframe {
        font-family: 'Fira Code', monospace !important;
        font-size: 0.85rem;
        background-color: #0a0a0a !important;
        color: #e5e5e5 !important;
    }
    
    /* Download button */
    .stDownloadButton button {
        width: 100%;
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        font-size: 0.875rem;
    }
    
    .stDownloadButton button:hover {
        background: #2563eb;
        transform: translateY(-1px);
    }
    
    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        background-color: #1a1a1a;
        border-color: #262626;
    }
    
    /* Divider */
    hr {
        margin: 2.5rem 0;
        border: none;
        height: 1px;
        background: #262626;
    }
    
    /* Warning message */
    .stWarning {
        background: #422006;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #fbbf24;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA LOADING ====================
@st.cache_data
def load_master_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="results")
    for c in ["n_balls", "mean_residual", "std_residual", "se", "t_stat"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["BatterID"] = df["BatterID"].astype(str)
    df["bowling_type"] = df["bowling_type"].astype(str)
    df = df.dropna(subset=["BatterID", "bowling_type", "n_balls", "mean_residual", "t_stat"]).copy()
    return df

# Load unified file (pace + spin)
df = load_master_excel("batter_outperformance_master.xlsx")

# ==================== HEADER ====================
st.title("Batter Outperformance")
st.caption("Interactive exploration of batter performance relative to an OLS expected-runs baseline")

# ==================== SIDEBAR CONTROLS ====================
with st.sidebar:
    st.header("Filters")
    
    # Bowling type filter with custom pills
    st.markdown("**Bowling Type**")
    bowling_choice = st.multiselect(
        "Select bowling types",
        ["Pace", "Spin"],
        default=["Pace"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Minimum balls slider
    min_balls = int(df["n_balls"].min())
    max_balls = int(df["n_balls"].max())
    n_min = st.slider(
        "Minimum balls faced",
        min_value=min_balls,
        max_value=max_balls,
        value=100,
        step=10,
        help="Filter batters by minimum number of balls faced"
    )
    
    # T-stat threshold slider
    t_min = st.slider(
        "Minimum t-statistic",
        min_value=0.0,
        max_value=max(3.0, float(df["t_stat"].max())),
        value=2.0,
        step=0.1,
        help="Statistical significance threshold"
    )
    
    st.markdown("---")
    
    # Summary metrics
    st.markdown("### Dataset Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-label">Total Records</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df['BatterID'].nunique():,}</div>
            <div class="metric-label">Unique Batters</div>
        </div>
        """, unsafe_allow_html=True)

# ==================== FILTER DATA ====================
f = df[df["bowling_type"].isin(bowling_choice)].copy()
f = f[f["n_balls"] >= n_min]
f = f[f["t_stat"] >= t_min]
f = f[f["mean_residual"] > 0]

if f.empty:
    st.warning("⚠️ No batters match the current filters. Try adjusting your criteria.")
    st.stop()

# Elite flag (for color)
f["elite"] = f["t_stat"] >= 2

# ==================== MAIN CONTENT ====================
# Summary stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Filtered Batters", f"{len(f):,}")
with col2:
    st.metric("Elite Performers", f"{f['elite'].sum():,}", help="t-stat ≥ 2.0")
with col3:
    avg_residual = f["mean_residual"].mean()
    st.metric("Avg Outperformance", f"{avg_residual:.3f}")
with col4:
    avg_balls = f["n_balls"].mean()
    st.metric("Avg Balls Faced", f"{int(avg_balls):,}")

st.markdown("<br>", unsafe_allow_html=True)

# ==================== VISUALIZATION & TABLE ====================
left, right = st.columns([2, 1])

with left:
    st.subheader("Performance Visualization")
    
    title_suffix = " & ".join(bowling_choice) if bowling_choice else "None"
    
    # Create plotly scatter with dark theme styling
    fig = px.scatter(
        f,
        x="mean_residual",
        y="n_balls",
        size="t_stat",
        color="elite",
        symbol="bowling_type",
        color_discrete_map={
            True: "#3b82f6",    # elite - blue
            False: "#525252"    # other - gray
        },
        hover_name="BatterID",
        hover_data={
            "bowling_type": True,
            "mean_residual": ":.3f",
            "n_balls": True,
            "t_stat": ":.2f",
            "elite": False
        },
        title=f"Outperformance vs Volume ({title_suffix})",
        labels={
            "mean_residual": "Mean Residual (Runs)",
            "n_balls": "Balls Faced",
            "t_stat": "T-Statistic"
        }
    )
    
    # Update layout for dark theme
    fig.update_layout(
        plot_bgcolor="#0a0a0a",
        paper_bgcolor="#0a0a0a",
        font=dict(family="Inter, sans-serif", size=12, color="#e5e5e5"),
        title=dict(font=dict(size=15, color="#fafafa", family="Inter"), x=0),
        legend=dict(
            title=dict(text="Elite (t ≥ 2.0)", font=dict(size=11, color="#d4d4d4")),
            bgcolor="#111111",
            bordercolor="#262626",
            borderwidth=1,
            font=dict(color="#d4d4d4")
        ),
        hoverlabel=dict(
            bgcolor="#1a1a1a",
            font_size=12,
            font_family="Inter",
            bordercolor="#404040"
        ),
        margin=dict(t=40, b=50, l=50, r=20)
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#1a1a1a",
        zeroline=True,
        zerolinecolor="#404040",
        zerolinewidth=2,
        color="#a3a3a3"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#1a1a1a",
        color="#a3a3a3"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Leaderboard")
    
    sort_choice = st.selectbox(
        "Sort by",
        ["mean_residual", "t_stat", "n_balls"],
        format_func=lambda x: {
            "mean_residual": "📊 Outperformance",
            "t_stat": "⭐ Significance",
            "n_balls": "🎯 Volume"
        }[x],
        label_visibility="collapsed"
    )
    
    table = f.sort_values(sort_choice, ascending=False).reset_index(drop=True)
    table_disp = table[["BatterID", "bowling_type", "n_balls", "mean_residual", "t_stat"]].copy()
    table_disp.columns = ["Batter", "Type", "Balls", "Residual", "T-Stat"]
    table_disp["Residual"] = table_disp["Residual"].round(3)
    table_disp["T-Stat"] = table_disp["T-Stat"].round(2)
    
    st.dataframe(
        table_disp,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    st.download_button(
        "📥 Download Filtered Data",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name=f"batters_{title_suffix.replace(' & ', '_')}.csv",
        mime="text/csv"
    )

# ==================== FOOTER INFO ====================
st.divider()

col1, col2 = st.columns([3, 1])
with col1:
    st.caption(
        "💡 **Mean residual > 0** indicates scoring above expectation given ball tracking features. "
        "Use the bowling type filter to compare Pace vs Spin performance, or select both for combined analysis."
    )
with col2:
    if bowling_choice:
        st.caption(f"Currently viewing: **{', '.join(bowling_choice)}**")