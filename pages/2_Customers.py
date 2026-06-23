import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from utils import load_data,filter_delivered


st.set_page_config(page_title='Customer Analysis', 
                   page_icon= '👥', 
                   layout= 'wide',
                   initial_sidebar_state='expanded',
                   menu_items={
                       'Get help' : 'https://github.com/yaroslav-hezei/ecommerce-dashboard',
                       'Report a bug' : 'https://github.com/yaroslav-hezei/ecommerce-dashboard/issues'
                   })

st.title("Customer Analysis")


df = load_data()
df_for_pie = df.copy()
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
    df_filtered = df.copy()


# New vs Returning is a lifetime property of a customer, not something tied to the
# selected period — a customer's earlier order could fall outside the date range,
# which would wrongly classify them as "New". Use the full delivered history (df),
# not the period-sliced df_filtered.
customers_status = (
    df
    .groupby('customer_unique_id')['order_id']
    .nunique()
    .reset_index()
)

customers_status['type'] = np.where(customers_status['order_id'] > 1, 'Returning', 'New')
new_customers = (customers_status['type'] == 'New').sum()
returning_customers = (customers_status['type'] == 'Returning').sum()

col1, col2 = st.columns(2)

col1.metric(label = 'New Customers', value=new_customers,border= True)
col2.metric(label = 'Returning Customers', value=returning_customers, border= True)

# Same reasoning as above: a customer's true first order can only be found by
# looking at their full history, not a date-filtered slice.
first_orders = (df
                     .groupby('customer_unique_id')['order_purchase_timestamp']
                     .min()
                     .reset_index()
                )

first_orders['month'] = first_orders['order_purchase_timestamp'].dt.to_period('M').astype('str')

first_orders = first_orders.groupby('month')['customer_unique_id'].count().reset_index()

first_orders_fig = px.line(
    first_orders,
    x = 'month',
    y = 'customer_unique_id',
    title='New Customers Acquired Per Month',
    labels={'month': 'Month', 'customer_unique_id': 'New customers'}
)

with st.container(border=True):
    st.plotly_chart(first_orders_fig, use_container_width=True)
    st.caption("Reflects all-time customer acquisition, not filtered by the selected period.")


# pie
orders_status_distribution = df_for_pie.groupby('order_status')['order_id'].nunique().reset_index()

pie_fig = px.pie(orders_status_distribution,
                 names = 'order_status',
                 values = 'order_id',
                 title = 'Order Status Distribution',
                 )


timedelta = (
    df_filtered['order_delivered_customer_date']
    - df_filtered['order_purchase_timestamp']
).dt.days
df_filtered['delivery_days'] = timedelta


# --- Top 10 states by revenue — shared anchor so delivery time and Row 4 revenue chart agree ---
revenue_by_state = df_filtered.groupby('customer_state')['price'].sum().reset_index()
top10_states = revenue_by_state.nlargest(10, 'price')['customer_state']

# delivery_days is an order-level value (one delivery date per order), but df_filtered
# has one row per item — averaging directly would overweight multi-item orders.
# Drop duplicate order_ids first so every order counts exactly once in the mean.
delivery_by_order = df_filtered.drop_duplicates(subset='order_id')[['customer_state', 'delivery_days']]

# --- Avg delivery time, restricted to those same top 10 states (avoids small-sample noise) ---
delivery_by_state = delivery_by_order.groupby('customer_state')['delivery_days'].mean().reset_index()
top_10_orders_customers = delivery_by_state[delivery_by_state['customer_state'].isin(top10_states)]
top_10_orders_customers = top_10_orders_customers.sort_values(by='delivery_days', ascending=True)  # ascending for readable horizontal bar

top10_fig = px.bar(
    top_10_orders_customers,
    x='delivery_days',
    y='customer_state',
    orientation='h',
    title='Avg Delivery Time — Top 10 States by Revenue',
    labels={'delivery_days': 'Avg Delivery Days', 'customer_state': 'Customer State'}
)
col_left, col_right = st.columns(2)
with col_left:
    with st.container(border=True):
        st.plotly_chart(pie_fig, use_container_width=True)
        st.caption("Reflects all-time order status distribution, not filtered by the selected period.")
with col_right:
    with st.container(border=True):
        st.plotly_chart(top10_fig, use_container_width=True)

# --- Row 4: Revenue by state (top 10) ---
top10_revenue_by_state = revenue_by_state[revenue_by_state['customer_state'].isin(top10_states)]
top10_revenue_by_state = top10_revenue_by_state.sort_values(by='price', ascending=False)  # descending — vertical bar, не horizontal

revenue_state_fig = px.bar(
    top10_revenue_by_state,
    x='customer_state',
    y='price',
    title='Revenue by State (Top 10)',
    labels={'customer_state': 'Customer State', 'price': 'Revenue (R$)'}
)

with st.container(border=True):
    st.plotly_chart(revenue_state_fig, use_container_width=True)