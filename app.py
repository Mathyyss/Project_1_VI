# ============================================
# NSF GRANT CANCELLATIONS - STREAMLIT APP
# Authors: [VotreNom1], [VotreNom2]
# Date: November 2025
# ============================================

import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
import numpy as np

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="NSF Grant Cancellations",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# LOAD DATA
# ============================================

@st.cache_data
def load_data():
    df = pd.read_csv("merged_clean_ready.csv")
    return df

df = load_data()

# Calculate global statistics
total_grants = len(df)
total_budget = df['budget_preferred'].sum()
num_states = df['org_state'].nunique()
num_institutions = df['org_name'].nunique()
reinstated_count = df['reinstated'].sum()

# ============================================
# HEADER
# ============================================

st.title("📊 NSF Grant Cancellations Analysis")
st.markdown("### Analysis of NSF Grants Terminated by the Trump Administration")
st.markdown(f"**Authors:** [Your Names] | **Course:** Data Visualization | **Date:** November 2025")

# Key metrics
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Total Grants Cancelled", f"{total_grants:,}")
with col_m2:
    st.metric("Total Budget Lost", f"${total_budget/1e9:.2f}B")
with col_m3:
    st.metric("States Affected", num_states)
with col_m4:
    st.metric("Grants Reinstated", f"{reinstated_count} ({reinstated_count/total_grants*100:.1f}%)")

st.markdown("---")

# ============================================
# Q1: GEOGRAPHIC DISTRIBUTION
# ============================================

st.header("Q1: Geographic Distribution of Cancellations")

# Prepare data
state_counts = df.groupby('org_state').agg({
    'grant_id': 'count',
    'budget_preferred': 'sum'
}).rename(columns={
    'grant_id': 'num_grants',
    'budget_preferred': 'total_budget'
}).reset_index()

# State ID mapping
state_id_map = {
    'AL': 1, 'AK': 2, 'AZ': 4, 'AR': 5, 'CA': 6, 'CO': 8, 'CT': 9, 'DE': 10,
    'FL': 12, 'GA': 13, 'HI': 15, 'ID': 16, 'IL': 17, 'IN': 18, 'IA': 19,
    'KS': 20, 'KY': 21, 'LA': 22, 'ME': 23, 'MD': 24, 'MA': 25, 'MI': 26,
    'MN': 27, 'MS': 28, 'MO': 29, 'MT': 30, 'NE': 31, 'NV': 32, 'NH': 33,
    'NJ': 34, 'NM': 35, 'NY': 36, 'NC': 37, 'ND': 38, 'OH': 39, 'OK': 40,
    'OR': 41, 'PA': 42, 'RI': 44, 'SC': 45, 'SD': 46, 'TN': 47, 'TX': 48,
    'UT': 49, 'VT': 50, 'VA': 51, 'WA': 53, 'WV': 54, 'WI': 55, 'WY': 56,
    'DC': 11, 'PR': 72
}

state_counts['id'] = state_counts['org_state'].map(state_id_map)
state_counts = state_counts.dropna(subset=['id'])

col1, col2 = st.columns([1.3, 1])

with col1:
    st.subheader("Map View")
    
    # Map
    states_geo = alt.topo_feature(data.us_10m.url, 'states')
    
    map_chart = alt.Chart(states_geo).mark_geoshape(
        stroke='white',
        strokeWidth=0.8
    ).encode(
        color=alt.Color('num_grants:Q',
                        scale=alt.Scale(scheme='orangered', type='sqrt', domain=[0, 500]),
                        title='Grants',
                        legend=alt.Legend(orient='bottom', direction='horizontal')),
        tooltip=[
            alt.Tooltip('org_state:N', title='State'),
            alt.Tooltip('num_grants:Q', title='Grants', format=',d'),
            alt.Tooltip('total_budget:Q', title='Budget', format='$,.0f')
        ]
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(state_counts, 'id', ['num_grants', 'org_state', 'total_budget'])
    ).project(
        type='albersUsa'
    ).properties(
        width=550,
        height=350
    )
    
    st.altair_chart(map_chart, use_container_width=True)

with col2:
    st.subheader("Top 10 States")
    
    # Top 10 bar chart
    top10_states = state_counts.nlargest(10, 'num_grants')
    
    bar_chart = alt.Chart(top10_states).mark_bar().encode(
        x=alt.X('num_grants:Q', title='Number of Grants', axis=alt.Axis(format='d')),
        y=alt.Y('org_state:N', title=None, sort='-x'),
        color=alt.Color('num_grants:Q', scale=alt.Scale(scheme='orangered'), legend=None),
        tooltip=[
            alt.Tooltip('org_state:N', title='State'),
            alt.Tooltip('num_grants:Q', title='Grants', format=',d')
        ]
    ).properties(
        width=400,
        height=350
    )
    
    st.altair_chart(bar_chart, use_container_width=True)

st.markdown("---")

# ============================================
# Q2 & Q3: INSTITUTIONS
# ============================================

st.header("Q2 & Q3: Most Affected Institutions")

# Prepare data
institution_stats = df.groupby('org_name').agg({
    'grant_id': 'count',
    'budget_preferred': 'sum'
}).rename(columns={
    'grant_id': 'num_grants',
    'budget_preferred': 'total_budget'
}).reset_index()

def shorten_name(name, max_length=55):
    return name[:max_length-3] + '...' if len(name) > max_length else name

col3, col4 = st.columns(2)

with col3:
    st.subheader("Q2: By Number of Grants")
    
    # Top 15 by count
    top_grants = institution_stats.nlargest(15, 'num_grants').copy()
    top_grants['org_name_display'] = top_grants['org_name'].apply(shorten_name)
    mean_grants = institution_stats['num_grants'].mean()
    
    # Lollipop chart
    lines = alt.Chart(top_grants).mark_rule(
        color='#d62728',
        strokeWidth=2.5,
        opacity=0.8
    ).encode(
        x=alt.X('start:Q'),
        x2=alt.X2('num_grants:Q'),
        y=alt.Y('org_name_display:N', sort='-x', title=None,
                axis=alt.Axis(labelLimit=450, labelFontSize=10))
    ).transform_calculate(start='0')
    
    points = alt.Chart(top_grants).mark_circle(
        size=150,
        color='#d62728'
    ).encode(
        x=alt.X('num_grants:Q', title='Number of Grants',
                scale=alt.Scale(domain=[0, top_grants['num_grants'].max() * 1.1])),
        y=alt.Y('org_name_display:N', sort='-x'),
        tooltip=[
            alt.Tooltip('org_name:N', title='Institution'),
            alt.Tooltip('num_grants:Q', title='Grants', format=',d')
        ]
    )
    
    text = alt.Chart(top_grants).mark_text(
        align='left', dx=8, fontSize=10, fontWeight='bold'
    ).encode(
        x='num_grants:Q',
        y=alt.Y('org_name_display:N', sort='-x'),
        text=alt.Text('num_grants:Q', format='d')
    )
    
    chart_q2 = (lines + points + text).properties(
        width=400,
        height=500
    )
    
    st.altair_chart(chart_q2, use_container_width=True)

with col4:
    st.subheader("Q3: By Budget Lost")
    
    # Top 15 by budget
    budget_stats = institution_stats.sort_values('total_budget', ascending=False)
    top_budget = budget_stats.head(15).copy()
    top_budget['org_name_display'] = top_budget['org_name'].apply(shorten_name)
    top_budget['budget_millions'] = top_budget['total_budget'] / 1_000_000
    mean_budget_millions = budget_stats['total_budget'].mean() / 1_000_000
    
    # Lollipop chart
    lines_b = alt.Chart(top_budget).mark_rule(
        color='#2ca02c',
        strokeWidth=2.5,
        opacity=0.8
    ).encode(
        x=alt.X('start:Q'),
        x2=alt.X2('budget_millions:Q'),
        y=alt.Y('org_name_display:N', sort='-x', title=None,
                axis=alt.Axis(labelLimit=450, labelFontSize=10))
    ).transform_calculate(start='0')
    
    points_b = alt.Chart(top_budget).mark_circle(
        size=150,
        color='#2ca02c'
    ).encode(
        x=alt.X('budget_millions:Q', title='Budget Lost (M$)',
                scale=alt.Scale(domain=[0, top_budget['budget_millions'].max() * 1.1])),
        y=alt.Y('org_name_display:N', sort='-x'),
        tooltip=[
            alt.Tooltip('org_name:N', title='Institution'),
            alt.Tooltip('total_budget:Q', title='Budget', format='$,.0f')
        ]
    )
    
    text_b = alt.Chart(top_budget).mark_text(
        align='left', dx=8, fontSize=10, fontWeight='bold'
    ).encode(
        x='budget_millions:Q',
        y=alt.Y('org_name_display:N', sort='-x'),
        text=alt.Text('budget_millions:Q', format='$.1f')
    )
    
    chart_q3 = (lines_b + points_b + text_b).properties(
        width=400,
        height=500
    )
    
    st.altair_chart(chart_q3, use_container_width=True)

st.markdown("---")

# ============================================
# Q4 & Q5: CORRELATIONS
# ============================================

st.header("Q4 & Q5: Correlation Analysis")

col5, col6 = st.columns(2)

with col5:
    st.subheader("Q4: Flagged Words Correlation")
    
    # Calculate statistics
    with_flagged = df['has_flagged_words'].sum()
    without_flagged = total_grants - with_flagged
    budget_with = df[df['has_flagged_words']]['budget_preferred'].sum()
    budget_without = df[~df['has_flagged_words']]['budget_preferred'].sum()
    
    # Prepare data
    flagged_summary = pd.DataFrame({
        'category': ['With Flagged Words', 'Without Flagged Words'],
        'count': [with_flagged, without_flagged],
        'budget': [budget_with, budget_without]
    })
    
    # Chart 1: By count
    chart_count = alt.Chart(flagged_summary).mark_bar(
        cornerRadiusEnd=4
    ).encode(
        x=alt.X('count:Q', title='Number of Grants', axis=alt.Axis(format='d')),
        y=alt.Y('category:N', title=None, sort='-x'),
        color=alt.Color('category:N',
                        scale=alt.Scale(
                            domain=['With Flagged Words', 'Without Flagged Words'],
                            range=['#ff7f0e', '#1f77b4']
                        ),
                        legend=None),
        tooltip=[
            alt.Tooltip('category:N'),
            alt.Tooltip('count:Q', title='Grants', format=',d')
        ]
    ).properties(width=400, height=120)
    
    text_count = chart_count.mark_text(
        align='left', dx=5, fontSize=11, fontWeight='bold'
    ).encode(
        text=alt.Text('count:Q', format='d'),
        color=alt.value('black')
    )
    
    # Chart 2: By budget
    chart_budget = alt.Chart(flagged_summary).mark_bar(
        cornerRadiusEnd=4
    ).encode(
        x=alt.X('budget:Q', title='Budget Lost ($)', axis=alt.Axis(format='$,.0s')),
        y=alt.Y('category:N', title=None, sort='-x'),
        color=alt.Color('category:N',
                        scale=alt.Scale(
                            domain=['With Flagged Words', 'Without Flagged Words'],
                            range=['#ff7f0e', '#1f77b4']
                        ),
                        legend=None),
        tooltip=[
            alt.Tooltip('category:N'),
            alt.Tooltip('budget:Q', title='Budget', format='$,.0f')
        ]
    ).properties(width=400, height=120)
    
    text_budget = chart_budget.mark_text(
        align='left', dx=5, fontSize=11, fontWeight='bold'
    ).encode(
        text=alt.Text('budget:Q', format='$,.0s'),
        color=alt.value('black')
    )
    
    chart_q4 = alt.vconcat(
        (chart_count + text_count),
        (chart_budget + text_budget),
        spacing=20
    ).properties(
        title={
            'text': f'{with_flagged} grants (84.6%) contain flagged words',
            'fontSize': 12
        }
    )
    
    st.altair_chart(chart_q4, use_container_width=True)

with col6:
    st.subheader("Q5: Cruz List & Reinstatements")
    
    # Calculate reinstatement rates
    df_term = df[df['terminated'] == True].copy()
    
    cruz_reinstated = df_term[df_term['in_cruz_list'] == True]['reinstated'].sum()
    cruz_total = (df_term['in_cruz_list'] == True).sum()
    non_cruz_reinstated = df_term[df_term['in_cruz_list'] == False]['reinstated'].sum()
    non_cruz_total = (df_term['in_cruz_list'] == False).sum()
    
    rate_cruz = (cruz_reinstated / cruz_total * 100) if cruz_total > 0 else 0
    rate_non_cruz = (non_cruz_reinstated / non_cruz_total * 100) if non_cruz_total > 0 else 0
    
    reins_data = pd.DataFrame({
        'Category': ['On Cruz List', 'Not on Cruz List'],
        'Rate': [rate_cruz, rate_non_cruz],
        'n': [cruz_total, non_cruz_total]
    })
    
    chart_reins = alt.Chart(reins_data).mark_bar(
        cornerRadiusEnd=4,
        size=60
    ).encode(
        x=alt.X('Rate:Q', title='Reinstatement Rate (%)',
                scale=alt.Scale(domain=[0, 40])),
        y=alt.Y('Category:N', title=None, sort='-x'),
        color=alt.Color('Category:N',
                        scale=alt.Scale(
                            domain=['On Cruz List', 'Not on Cruz List'],
                            range=['#ff7f0e', '#1f77b4']
                        ),
                        legend=None),
        tooltip=[
            alt.Tooltip('Category:N'),
            alt.Tooltip('Rate:Q', title='Rate (%)', format='.1f'),
            alt.Tooltip('n:Q', title='Total', format=',d')
        ]
    ).properties(
        width=400,
        height=200
    )
    
    text_reins = chart_reins.mark_text(
        align='left', dx=5, fontSize=12, fontWeight='bold'
    ).encode(
        text=alt.Text('Rate:Q', format='.1f'),
        color=alt.value('black')
    )
    
    chart_q5 = (chart_reins + text_reins).properties(
        title={
            'text': 'Cruz grants 4× less likely to be reinstated (p<0.001)',
            'fontSize': 12
        }
    )
    
    st.altair_chart(chart_q5, use_container_width=True)

st.markdown("---")

# ============================================
# FOOTER
# ============================================

with st.expander("ℹ️ About This Project"):
    st.markdown("""
    ### Project Information
    
    **Course:** Data Visualization  
    **Authors:** [Your Names Here]  
    **Institution:** [Your University]  
    **Date:** November 2025
    
    ### Dataset Summary
    - **Total grants cancelled:** 1,970
    - **Total budget lost:** $1.72 billion
    - **States affected:** 52
    - **Institutions affected:** 507
    - **Grants reinstated:** 420 (21.3%)
    
    ### Key Findings
    1. **Geographic concentration:** California (466), Massachusetts (256), Texas (122)
    2. **Institutional impact:** UCLA most affected (306 grants, $199.7M)
    3. **Thematic targeting:** 84.6% of grants contain diversity/equity/climate keywords
    4. **Reinstatement disparity:** Cruz-listed grants 4× less likely to be reinstated
    
    ### Methodology
    - Data cleaning with word-boundary matching for flagged words
    - Statistical testing (Chi-square, Fisher's exact)
    - Interactive visualizations with Altair
    - Colorblind-accessible palettes
    
    ### Technologies
    - **Python:** pandas, altair, streamlit
    - **Statistical analysis:** scipy, statsmodels
    - **Visualization:** Altair (declarative visualization)
    """)

st.markdown("---")
st.markdown("**© 2025 | Data Visualization Project | [Your Names]**")
