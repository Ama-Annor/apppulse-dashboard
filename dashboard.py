"""
AppPulse Business Insights Dashboard
Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AppPulse - Business Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with increased font sizes
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
        font-size: 30px;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stMetric label {
        font-size: 26px !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 42px !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 22px !important;
    }
    h1 {
        color: #667eea;
        font-size: 58px !important;
    }
    h2 {
        font-size: 52px !important;
    }
    h3 {
        font-size: 42px !important;
    }
    p, .stMarkdown, div {
        font-size: 30px !important;
    }
    .success-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
    }
    .success-card h4 {
        font-size: 36px !important;
    }
    .success-card p {
        font-size: 30px !important;
    }
    .stDataFrame {
        font-size: 30px !important;
    }
    .stDataFrame th {
        font-size: 30px !important;
    }
    .stDataFrame td {
        font-size: 30px !important;
    }
    .sidebar .sidebar-content {
        font-size: 30px !important;
    }
    .stSelectbox label, .stSlider label, .stTextInput label {
        font-size: 30px !important;
    }
    .stTab {
        font-size: 32px !important;
    }
    button {
        font-size: 30px !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data
def load_data():
    """Load app data"""
    try:
        # Try to load from multiple possible locations
        df = pd.read_csv('apps_with_features.csv')
        return df
    except:
        try:
            df = pd.read_csv('data/apps_with_features.csv')
            return df
        except:
            st.error(" Data file not found. Please place 'apps_with_features.csv' in the app directory.")
            return None

# Load data
df = load_data()

if df is None:
    st.stop()

# =============================================================================
# SIDEBAR - FILTERS
# =============================================================================

st.sidebar.image("https://img.icons8.com/fluency/96/000000/google-play.png", width=80)
st.sidebar.title(" AppPulse Dashboard")
st.sidebar.markdown("---")

# Filters
st.sidebar.header(" Filters")

# Category filter
categories = ['All Categories'] + sorted(df['Category'].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

# Type filter
app_types = ['All Types', 'Free', 'Paid']
selected_type = st.sidebar.selectbox("Type", app_types)

# Rating filter
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)

# Review count filter
min_reviews = st.sidebar.slider("Minimum Reviews", 0, 10000, 0, 100)

# Apply filters
df_filtered = df.copy()

if selected_category != 'All Categories':
    df_filtered = df_filtered[df_filtered['Category'] == selected_category]

if selected_type != 'All Types':
    df_filtered = df_filtered[df_filtered['Type'] == selected_type]

df_filtered = df_filtered[df_filtered['Rating'] >= min_rating]
df_filtered = df_filtered[df_filtered['Reviews'] >= min_reviews]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing:** {len(df_filtered):,} / {len(df):,} apps")

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

# Header
st.title(" AppPulse Business Intelligence Dashboard")
st.markdown("---")

# =============================================================================
# KEY METRICS
# =============================================================================

st.header(" Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Apps",
        value=f"{len(df_filtered):,}",
        delta=f"{len(df_filtered) - len(df)}" if selected_category != 'All Categories' else None
    )

with col2:
    avg_rating = df_filtered['Rating'].mean()
    st.metric(
        label="Average Rating",
        value=f"{avg_rating:.2f} ",
        delta=f"{avg_rating - df['Rating'].mean():+.2f}" if len(df_filtered) < len(df) else None
    )

with col3:
    total_installs = df_filtered['Installs_Clean'].sum()
    st.metric(
        label="Total Installs",
        value=f"{total_installs/1e9:.1f}B" if total_installs > 1e9 else f"{total_installs/1e6:.0f}M"
    )

with col4:
    free_percentage = (df_filtered['Type'] == 'Free').sum() / len(df_filtered) * 100
    st.metric(
        label="Free Apps",
        value=f"{free_percentage:.1f}%"
    )

st.markdown("---")

# =============================================================================
# CATEGORY ANALYSIS
# =============================================================================

st.header(" Category Analysis")

# Category performance
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Categories by App Count")
    
    category_counts = df_filtered['Category'].value_counts().head(10)
    
    fig = px.bar(
        x=category_counts.values,
        y=category_counts.index,
        orientation='h',
        labels={'x': 'Number of Apps', 'y': 'Category'},
        color=category_counts.values,
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis={'categoryorder': 'total ascending'},
        font=dict(size=20),
        xaxis_title_font=dict(size=22),
        yaxis_title_font=dict(size=22)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Average Rating by Category")
    
    category_ratings = df_filtered.groupby('Category')['Rating'].mean().sort_values(ascending=False).head(10)
    
    fig = px.bar(
        x=category_ratings.values,
        y=category_ratings.index,
        orientation='h',
        labels={'x': 'Average Rating', 'y': 'Category'},
        color=category_ratings.values,
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis={'categoryorder': 'total ascending'},
        font=dict(size=20),
        xaxis_title_font=dict(size=22),
        yaxis_title_font=dict(size=22)
    )
    st.plotly_chart(fig, use_container_width=True)

# Category details table
st.subheader(" Category Performance Summary")

category_summary = df_filtered.groupby('Category').agg({
    'App': 'count',
    'Rating': 'mean',
    'Reviews': 'sum',
    'Installs_Clean': 'sum'
}).round(2)

category_summary.columns = ['App Count', 'Avg Rating', 'Total Reviews', 'Total Installs']
category_summary = category_summary.sort_values('App Count', ascending=False)

st.dataframe(
    category_summary.style.format({
        'App Count': '{:,.0f}',
        'Avg Rating': '{:.2f}',
        'Total Reviews': '{:,.0f}',
        'Total Installs': '{:,.0f}'
    }),
    use_container_width=True
)

st.markdown("---")

# =============================================================================
# RATING ANALYSIS
# =============================================================================

st.header(" Rating Distribution & Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Rating Distribution")
    
    fig = px.histogram(
        df_filtered,
        x='Rating',
        nbins=20,
        labels={'Rating': 'App Rating', 'count': 'Number of Apps'},
        color_discrete_sequence=['#667eea']
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        font=dict(size=20),
        xaxis_title_font=dict(size=22),
        yaxis_title_font=dict(size=22)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Rating vs Reviews")
    
    # Sample for performance
    sample_df = df_filtered.sample(min(1000, len(df_filtered)))
    
    fig = px.scatter(
        sample_df,
        x='Reviews',
        y='Rating',
        color='Type',
        size='Installs_Clean',
        hover_data=['App', 'Category'],
        labels={'Reviews': 'Number of Reviews', 'Rating': 'App Rating'},
        color_discrete_map={'Free': '#10b981', 'Paid': '#3b82f6'}
    )
    fig.update_layout(
        height=400,
        xaxis_type="log",
        font=dict(size=20),
        xaxis_title_font=dict(size=22),
        yaxis_title_font=dict(size=22),
        legend_font=dict(size=20)
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =============================================================================
# SENTIMENT ANALYSIS
# =============================================================================

st.header(" Sentiment Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    avg_polarity = df_filtered['sentiment_polarity_mean'].mean()
    st.metric(
        label="Average Sentiment",
        value=f"{avg_polarity:.2f}",
        delta="Positive" if avg_polarity > 0 else "Negative"
    )

with col2:
    avg_positive = df_filtered['positive_percentage'].mean()
    st.metric(
        label="Positive Reviews",
        value=f"{avg_positive:.1f}%"
    )

with col3:
    avg_negative = df_filtered['negative_percentage'].mean()
    st.metric(
        label="Negative Reviews",
        value=f"{avg_negative:.1f}%"
    )

# Sentiment distribution
st.subheader("Sentiment Distribution by Category")

sentiment_by_category = df_filtered.groupby('Category').agg({
    'positive_percentage': 'mean',
    'negative_percentage': 'mean'
}).reset_index()

sentiment_by_category = sentiment_by_category.sort_values('positive_percentage', ascending=False).head(10)

fig = go.Figure()
fig.add_trace(go.Bar(
    name='Positive %',
    x=sentiment_by_category['Category'],
    y=sentiment_by_category['positive_percentage'],
    marker_color='#10b981'
))
fig.add_trace(go.Bar(
    name='Negative %',
    x=sentiment_by_category['Category'],
    y=sentiment_by_category['negative_percentage'],
    marker_color='#ef4444'
))

fig.update_layout(
    barmode='group',
    height=400,
    xaxis_title="Category",
    yaxis_title="Percentage",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    font=dict(size=20),
    xaxis_title_font=dict(size=22),
    yaxis_title_font=dict(size=22),
    legend_font=dict(size=20)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =============================================================================
# TOP PERFORMERS
# =============================================================================

st.header("🏆 Top Performing Apps")

tab1, tab2, tab3 = st.tabs(["By Rating", "By Installs", "By Reviews"])

with tab1:
    st.subheader("Highest Rated Apps")
    top_rated = df_filtered.nlargest(10, 'Rating')[['App', 'Category', 'Rating', 'Reviews', 'Type']]
    st.dataframe(top_rated, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Most Installed Apps")
    top_installs = df_filtered.nlargest(10, 'Installs_Clean')[['App', 'Category', 'Rating', 'Installs_Clean', 'Type']]
    st.dataframe(top_installs, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Most Reviewed Apps")
    top_reviews = df_filtered.nlargest(10, 'Reviews')[['App', 'Category', 'Rating', 'Reviews', 'Type']]
    st.dataframe(top_reviews, use_container_width=True, hide_index=True)

st.markdown("---")

# =============================================================================
# SUCCESS FACTORS
# =============================================================================

st.header(" Success Factor Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Price vs Rating")
    
    price_rating = df_filtered.groupby(pd.cut(df_filtered['Price_Clean'], bins=[0, 0.01, 2, 5, 10, 100]))['Rating'].mean()
    
    fig = px.bar(
        x=['Free', '$0-2', '$2-5', '$5-10', '$10+'],
        y=price_rating.values,
        labels={'x': 'Price Range', 'y': 'Average Rating'},
        color=price_rating.values,
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        font=dict(size=20),
        xaxis_title_font=dict(size=22),
        yaxis_title_font=dict(size=22)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Size vs Rating")
    
    size_rating = df_filtered.groupby(pd.cut(df_filtered['Size_MB'], bins=[0, 10, 50, 100, 500]))['Rating'].mean()
    
    fig = px.bar(
        x=['<10MB', '10-50MB', '50-100MB', '>100MB'],
        y=size_rating.values,
        labels={'x': 'App Size', 'y': 'Average Rating'},
        color=size_rating.values,
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        font=dict(size=20),
        xaxis_title_font=dict(size=22),
        yaxis_title_font=dict(size=22)
    )
    st.plotly_chart(fig, use_container_width=True)

# Key insights
st.subheader(" Key Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="success-card">
        <h4> Content Rating</h4>
        <p>Apps rated "Everyone" have highest average rating</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="success-card">
        <h4> Pricing Strategy</h4>
        <p>Free apps dominate but paid apps ($0-2) have higher ratings</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="success-card">
        <h4> Sentiment Impact</h4>
        <p>Positive sentiment correlates strongly with high ratings</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =============================================================================
# DATA EXPLORER
# =============================================================================

st.header(" Data Explorer")

st.subheader("Search Apps")
search_query = st.text_input("Enter app name to search", "")

if search_query:
    search_results = df_filtered[df_filtered['App'].str.contains(search_query, case=False, na=False)]
    st.write(f"Found {len(search_results)} apps")
    st.dataframe(
        search_results[['App', 'Category', 'Rating', 'Reviews', 'Installs_Clean', 'Type', 'Price_Clean']].head(20),
        use_container_width=True,
        hide_index=True
    )

# Raw data viewer
with st.expander(" View Raw Data"):
    st.dataframe(df_filtered.head(100), use_container_width=True)
    
    # Download button
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label=" Download Filtered Data as CSV",
        data=csv,
        file_name="apppulse_filtered_data.csv",
        mime="text/csv"
    )

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>AppPulse Business Intelligence Dashboard</p>
    <p>Individual Project by Ama Ansongmaa Aseda Annor | CS 452 - Machine Learning | December 2025</p>
    <p>Powered by Streamlit & Machine Learning</p>
</div>
""", unsafe_allow_html=True)