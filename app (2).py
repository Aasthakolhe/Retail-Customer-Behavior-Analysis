import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Retail Customer Behavior Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# ---------------------------------------------------------
# Load & clean data (same steps as the Jupyter notebook)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("customer_shopping_behavior.csv")

    # Fill missing review ratings with category median
    df['Review Rating'] = df.groupby('Category')['Review Rating'].transform(
        lambda x: x.fillna(x.median())
    )

    # Standardize column names to snake_case
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount'})

    # Feature engineering: age_group
    labels = ['Young Adult', 'Adult', 'Middle-aged', 'Senior']
    df['age_group'] = pd.qcut(df['age'], q=4, labels=labels)

    # Feature engineering: purchase_frequency_days
    frequency_mapping = {
        'Fortnightly': 14, 'Weekly': 7, 'Monthly': 30,
        'Quarterly': 90, 'Bi-Weekly': 14, 'Annually': 365,
        'Every 3 Months': 90
    }
    df['purchase_frequency_days'] = df['frequency_of_purchases'].map(frequency_mapping)

    # Drop redundant column if present
    if 'promo_code_used' in df.columns:
        df = df.drop('promo_code_used', axis=1)

    return df

df = load_data()

# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
st.sidebar.header("🔍 Filters")

subscription_filter = st.sidebar.multiselect(
    "Subscription Status",
    options=df['subscription_status'].unique(),
    default=df['subscription_status'].unique()
)

gender_filter = st.sidebar.multiselect(
    "Gender",
    options=df['gender'].unique(),
    default=df['gender'].unique()
)

category_filter = st.sidebar.multiselect(
    "Category",
    options=df['category'].unique(),
    default=df['category'].unique()
)

shipping_filter = st.sidebar.multiselect(
    "Shipping Type",
    options=df['shipping_type'].unique(),
    default=df['shipping_type'].unique()
)

# Apply filters
filtered_df = df[
    (df['subscription_status'].isin(subscription_filter)) &
    (df['gender'].isin(gender_filter)) &
    (df['category'].isin(category_filter)) &
    (df['shipping_type'].isin(shipping_filter))
]

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title("🛍️ Retail Customer Behavior Dashboard")
st.markdown("Interactive dashboard built from the retail customer behavior analysis project.")

# ---------------------------------------------------------
# KPI row
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Number of Customers", f"{filtered_df.shape[0]:,}")
col2.metric("Average Purchase Amount", f"${filtered_df['purchase_amount'].mean():.2f}")
col3.metric("Average Review Rating", f"{filtered_df['review_rating'].mean():.2f}")

st.markdown("---")

# ---------------------------------------------------------
# Row 1: Subscription pie + Revenue by category + Sales by category
# ---------------------------------------------------------
c1, c2, c3 = st.columns(3)

with c1:
    sub_counts = filtered_df['subscription_status'].value_counts().reset_index()
    sub_counts.columns = ['subscription_status', 'count']
    fig = px.pie(sub_counts, names='subscription_status', values='count',
                 title="Customers by Subscription Status", hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    rev_cat = filtered_df.groupby('category')['purchase_amount'].sum().reset_index()
    fig = px.bar(rev_cat, x='category', y='purchase_amount',
                 title="Revenue by Category")
    st.plotly_chart(fig, use_container_width=True)

with c3:
    sales_cat = filtered_df.groupby('category').size().reset_index(name='orders')
    fig = px.bar(sales_cat, x='category', y='orders',
                 title="Sales (Orders) by Category")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Row 2: Revenue by age group + Sales by age group
# ---------------------------------------------------------
c4, c5 = st.columns(2)

with c4:
    rev_age = filtered_df.groupby('age_group')['purchase_amount'].sum().reset_index()
    fig = px.bar(rev_age, x='purchase_amount', y='age_group', orientation='h',
                 title="Revenue by Age Group")
    st.plotly_chart(fig, use_container_width=True)

with c5:
    sales_age = filtered_df.groupby('age_group').size().reset_index(name='orders')
    fig = px.bar(sales_age, x='orders', y='age_group', orientation='h',
                 title="Sales (Orders) by Age Group")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Raw data (optional)
# ---------------------------------------------------------
with st.expander("📄 View Filtered Data"):
    st.dataframe(filtered_df)

st.markdown("---")
st.caption("Built with Streamlit · Data cleaned and analyzed using Python, SQL & Power BI")
