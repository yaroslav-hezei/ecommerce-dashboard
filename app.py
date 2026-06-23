import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_data,filter_delivered


st.set_page_config(page_title='Sales Dashboard', 
                   page_icon= '💼', 
                   layout= 'wide',
                   initial_sidebar_state='expanded',
                   menu_items={
                       'Get help' : 'https://github.com/yaroslav-hezei/ecommerce-dashboard',
                       'Report a bug' : 'https://github.com/yaroslav-hezei/ecommerce-dashboard/issues'
                   })

st.title("Sales Dashboard")

df = load_data()
df = filter_delivered(df)

min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()
date_range = st.sidebar.date_input('Period', value=(min_date,max_date),
                                   min_value=min_date,
                                   max_value=max_date)

# date_input yields a 1-tuple while the user is mid-selection (start picked, end not yet); unpacking would crash.
if len(date_range) == 2:
    start, end = date_range
    # Streamlit's quick-select presets (e.g. "This month") can push the chosen
    # range outside the widget's min/max_value, producing an empty mask.
    start = max(start, min_date.date())
    end = min(end, max_date.date())

    mask = (df['order_purchase_timestamp'].dt.date >= start) & (df['order_purchase_timestamp'].dt.date <= end)

    df_filtered = df[mask]
else: 
    # .copy() so that adding the 'weekday' column below doesn't mutate the cached df.
    df_filtered = df.copy()


total_revenue = df_filtered['price'].sum()
# nunique() because joining order_items fans out one row per item, so each order_id appears multiple times.
total_orders = df_filtered['order_id'].nunique()
avg_order_revenue = round(total_revenue / total_orders, 2)
# customer_unique_id deduplicates repeat buyers; customer_id is a per-order surrogate that changes each purchase.
unique_customers = df_filtered['customer_unique_id'].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric(label = 'Total Revenue', value= f"R$ {total_revenue:,.0f}" ,border= True)
col2.metric(label = 'Total Orders', value= total_orders, border= True)
col3.metric(label = 'AVG order revenue', value= avg_order_revenue, border= True)
col4.metric(label = 'Unique Customers', value= unique_customers, border= True)

monthly_revenue = df_filtered.groupby('month')['price'].sum().reset_index()

fig = px.line(
    monthly_revenue,
    x = 'month',
    y = 'price',
    title='Monthly Revenue',
    labels={'month': 'Month', 'price': 'Revenue (R$)'}
)

with st.container(border=True):
    st.plotly_chart(fig, use_container_width=True)

top_categories = (
    df_filtered.groupby('product_category_name_english')['price']
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

fig_cat = px.bar(
    top_categories,
    x = 'price',
    y = 'product_category_name_english',
    orientation='h',
    title='Top 5 Categories by Revenue',
    labels={'price': 'Revenue (R$)', 'product_category_name_english': 'Category'}
)

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

df_filtered['weekday'] = df_filtered['order_purchase_timestamp'].dt.day_name()
orders_by_day = df_filtered.groupby('weekday')['order_id'].nunique().reset_index()

# pd.Categorical enforces the Monday–Sunday order; without it, groupby sorts alphabetically (Friday first, etc.).
orders_by_day['weekday'] = pd.Categorical(orders_by_day['weekday'],
                                          categories=day_order,
                                          ordered=True)
orders_by_day = orders_by_day.sort_values('weekday')

fig_day = px.bar(
    orders_by_day,
    x='weekday',
    y='order_id',
    title='Orders by Day of Week',
    labels={'weekday': 'Day', 'order_id': 'Orders'}
)

col_left, col_right = st.columns(2)

with col_left:
    with st.container(border=True):
        st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    with st.container(border=True):
        st.plotly_chart(fig_day, use_container_width=True)


