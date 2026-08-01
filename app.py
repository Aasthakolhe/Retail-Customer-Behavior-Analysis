import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Retail Customer Behavior Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom CSS styling
# ---------------------------------------------------------
st.markdown("""
    <style>
        /* Overall background */
        .main {
            background-color: #0e1117;
        }

        /* KPI cards */
        .kpi-card {
            background: linear-gradient(135deg, #7b2ff7 0%, #d6249f 100%);
            padding: 22px 20px;
            border-radius: 14px;
            text-align: center;
            box-shadow: 0 4px 14px rgba(0,0,0,0.25);
        }
        .kpi-label {
            font-size: 14px;
            color: rgba(255,255,255,0.85);
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 32px;
            color: white;
            font-weight: 700;
        }

        /* Section headers */
        .section-title {
            font-size: 20px;
            font-weight: 700;
            color: #f0f0f0;
            margin-top: 10px;
            margin-bottom: 4px;
            border-left: 5px solid #d6249f;
            padding-left: 10px;
        }

        /* Chart containers */
        .chart-box {
            background-color: #161a23;
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }

        /* Hero header */
        .hero {
            padding: 24px 30px;
            border-radius: 16px;
            background: linear-gradient(120deg, #241b3f 0%, #3b1a4f 60%, #4a1942 100%);
            margin-bottom: 18px;
        }
        .hero h1 {
            color: white;
            font-size: 34px;
            margin: 0;
        }
        .hero p {
            color: rgba(255,255,255,0.75);
            font-size: 15px;
            margin-top: 6px;
        }

        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = "plotly_dark"
COLOR_SEQUENCE = ["#d6249f", "#a12ee0", "#7b2ff7", "#3e8ef7", "#22c1c3"]

# ---------------------------------------------------------
# Load & clean data (same steps as the Jupyter notebook)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("customer_shopping_behavior.csv")

    df['Review Rating'] = df.groupby('Category')['Review Rating'].transform(
        lambda x: x.fillna(x.median())
    )

    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount'})

    labels = ['Young Adult', 'Adult', 'Middle-aged', 'Senior']
    df['age_group'] = pd.qcut(df['age'], q=4, labels=labels)

    frequency_mapping = {
        'Fortnightly': 14, 'Weekly': 7, 'Monthly': 30,
        'Quarterly': 90, 'Bi-Weekly': 14, 'Annually': 365,
        'Every 3 Months': 90
    }
    df['purchase_frequency_days'] = df['frequency_of_purchases'].map(frequency_mapping)

    if 'promo_code_used' in df.columns:
        df = df.drop('promo_code_used', axis=1)

    return df

df = load_data()

# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔍 Filters")

    subscription_filter = st.multiselect(
        "Subscription Status",
        options=df['subscription_status'].unique(),
        default=df['subscription_status'].unique()
    )

    gender_filter = st.multiselect(
        "Gender",
        options=df['gender'].unique(),
        default=df['gender'].unique()
    )

    category_filter = st.multiselect(
        "Category",
        options=df['category'].unique(),
        default=df['category'].unique()
    )

    shipping_filter = st.multiselect(
        "Shipping Type",
        options=df['shipping_type'].unique(),
        default=df['shipping_type'].unique()
    )

    st.markdown("---")
    st.caption("Built with Streamlit · Python · Power BI · SQL")

filtered_df = df[
    (df['subscription_status'].isin(subscription_filter)) &
    (df['gender'].isin(gender_filter)) &
    (df['category'].isin(category_filter)) &
    (df['shipping_type'].isin(shipping_filter))
]

# ---------------------------------------------------------
# Hero header
# ---------------------------------------------------------
st.markdown("""
    <div class="hero">
        <h1>🛍️ Retail Customer Behavior Dashboard</h1>
        <p>Interactive exploration of customer demographics, revenue, and product performance</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI row
# ---------------------------------------------------------
if filtered_df.empty:
    st.warning("No data matches the selected filters. Try adjusting them in the sidebar.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Customers</div>
            <div class="kpi-value">{filtered_df.shape[0]:,}</div>
        </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Purchase</div>
            <div class="kpi-value">${filtered_df['purchase_amount'].mean():.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Review Rating</div>
            <div class="kpi-value">{filtered_df['review_rating'].mean():.2f} ⭐</div>
        </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">${filtered_df['purchase_amount'].sum():,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# ---------------------------------------------------------
# Row 1: Subscription pie + Revenue by category + Sales by category
# ---------------------------------------------------------
st.markdown('<div class="section-title">Category & Subscription Insights</div>', unsafe_allow_html=True)
st.write("")

c1, c2, c3 = st.columns(3)

with c1:
    sub_counts = filtered_df['subscription_status'].value_counts().reset_index()
    sub_counts.columns = ['subscription_status', 'count']
    fig = px.pie(
        sub_counts, names='subscription_status', values='count',
        title="Customers by Subscription Status", hole=0.55,
        color_discrete_sequence=COLOR_SEQUENCE, template=PLOTLY_TEMPLATE
    )
    fig.update_layout(margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    rev_cat = filtered_df.groupby('category')['purchase_amount'].sum().reset_index()
    fig = px.bar(
        rev_cat, x='category', y='purchase_amount',
        title="Revenue by Category", color='category',
        color_discrete_sequence=COLOR_SEQUENCE, template=PLOTLY_TEMPLATE
    )
    fig.update_layout(showlegend=False, margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

with c3:
    sales_cat = filtered_df.groupby('category').size().reset_index(name='orders')
    fig = px.bar(
        sales_cat, x='category', y='orders',
        title="Sales (Orders) by Category", color='category',
        color_discrete_sequence=COLOR_SEQUENCE, template=PLOTLY_TEMPLATE
    )
    fig.update_layout(showlegend=False, margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Row 2: Revenue by age group + Sales by age group
# ---------------------------------------------------------
st.markdown('<div class="section-title">Age Group Insights</div>', unsafe_allow_html=True)
st.write("")

c4, c5 = st.columns(2)

with c4:
    rev_age = filtered_df.groupby('age_group', observed=True)['purchase_amount'].sum().reset_index()
    fig = px.bar(
        rev_age, x='purchase_amount', y='age_group', orientation='h',
        title="Revenue by Age Group", color='age_group',
        color_discrete_sequence=COLOR_SEQUENCE, template=PLOTLY_TEMPLATE
    )
    fig.update_layout(showlegend=False, margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

with c5:
    sales_age = filtered_df.groupby('age_group', observed=True).size().reset_index(name='orders')
    fig = px.bar(
        sales_age, x='orders', y='age_group', orientation='h',
        title="Sales (Orders) by Age Group", color='age_group',
        color_discrete_sequence=COLOR_SEQUENCE, template=PLOTLY_TEMPLATE
    )
    fig.update_layout(showlegend=False, margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Row 3: Top products + Discount usage
# ---------------------------------------------------------
st.markdown('<div class="section-title">Product Performance</div>', unsafe_allow_html=True)
st.write("")

c6, c7 = st.columns(2)

with c6:
    top_rated = (
        filtered_df.groupby('item_purchased')['review_rating']
        .mean().reset_index()
        .sort_values('review_rating', ascending=False)
        .head(5)
    )
    fig = px.bar(
        top_rated, x='review_rating', y='item_purchased', orientation='h',
        title="Top 5 Products by Average Rating", color='item_purchased',
        color_discrete_sequence=COLOR_SEQUENCE, template=PLOTLY_TEMPLATE
    )
    fig.update_layout(showlegend=False, margin=dict(t=50, b=10, l=10, r=10),
                       yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

with c7:
    disc = filtered_df.groupby('item_purchased')['discount_applied'].apply(
        lambda x: (x == 'Yes').mean() * 100
    ).reset_index(name='discount_rate').sort_values('discount_rate', ascending=False).head(5)
    fig = px.bar(
        disc, x='discount_rate', y='item_purchased', orientation='h',
        title="Top 5 Discount-Dependent Products (%)", color='item_purchased',
        color_discrete_sequence=COLOR_SEQUENCE, template=PLOTLY_TEMPLATE
    )
    fig.update_layout(showlegend=False, margin=dict(t=50, b=10, l=10, r=10),
                       yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Raw data
# ---------------------------------------------------------
with st.expander("📄 View Filtered Data"):
    st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.caption("Built with Streamlit · Data cleaned and analyzed using Python, SQL & Power BI · by Aastha Kolhe")yzed using Python, SQL & Power BI")
