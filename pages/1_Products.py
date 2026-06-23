import streamlit as st
import plotly.express as px

from utils import load_data,filter_delivered

st.set_page_config(page_title='Product Analysis', 
                   page_icon= '🏷️', 
                   layout= 'wide',
                   initial_sidebar_state='expanded',
                   menu_items={
                       'Get help' : 'https://github.com/yaroslav-hezei/ecommerce-dashboard',
                       'Report a bug' : 'https://github.com/yaroslav-hezei/ecommerce-dashboard/issues'
                   })

st.title('Product Analysis')

df = load_data()
df = filter_delivered(df)  # restrict analysis to completed orders only

# sidebar filter — show all categories when nothing is selected
selected_categories = st.sidebar.multiselect(
    'Category',
    options= df['product_category_name_english'].unique()
)

if len(selected_categories) == 0:
    df_filtered = df.copy()
else:
    mask = df['product_category_name_english'].isin(selected_categories)
    df_filtered = df[mask]

# --- Top 10 categories by total revenue ---
category_revenue = df_filtered.groupby('product_category_name_english')['price'].sum().reset_index()

top10_categories = category_revenue.nlargest(10, 'price')
top10_categories = top10_categories.sort_values(by = 'price',ascending=True)  # ascending for readable horizontal bar

top10_fig = px.bar(top10_categories,
                   x = 'price',
                   y = 'product_category_name_english',
                   orientation= 'h',
                   title='Top 10 Categories by Revenue',
                   labels={'price': 'Revenue (R$)', 'product_category_name_english': 'Category'}
                   )

with st.container(border=True):
    st.plotly_chart(top10_fig, use_container_width= True)

# --- Scatter: avg price vs avg review score ---
category_price_review = df_filtered.groupby('product_category_name_english')[['price','review_score']].mean().reset_index()

scatter_fig = px.scatter(category_price_review,
                         x = 'price',
                         y = 'review_score',
                         title = 'Avg Price vs Avg Review Score by Category',
                         labels= {'price' : 'AVG Price (R$)', 'review_score' : 'Review Score'},
                         hover_data = ['product_category_name_english']
                         )

# --- Bottom 10 categories by total revenue ---
bottom10_categories = category_revenue.nsmallest(10, 'price')

bottom10_fig = px.bar(bottom10_categories,
                      x = 'price',
                      y = 'product_category_name_english',
                      orientation= 'h',
                      title= 'Bottom 10 Categories by Revenue',
                      labels = {'price' : 'Revenue (R$)', 'product_category_name_english': 'Category'})

col_left, col_right = st.columns(2)
with col_left:
    with st.container(border=True):
        st.plotly_chart(scatter_fig, use_container_width=True)
with col_right:
    with st.container(border=True):
        st.plotly_chart(bottom10_fig, use_container_width=True)


# --- Summary table: key metrics per category ---
summary_table = df_filtered.groupby('product_category_name_english').agg(
    revenue = ('price', 'sum'),
    orders = ('order_id', 'nunique'),
    avg_price = ('price', 'mean'),
    avg_review_score = ('review_score', 'mean')
).reset_index()

with st.container(border=True):
    st.dataframe(summary_table, use_container_width=True,
                 column_config={
                    'product_category_name_english': st.column_config.TextColumn('Category'),
                    'revenue': st.column_config.NumberColumn('Revenue (R$)', format='%.2f'),
                    'avg_price': st.column_config.NumberColumn('Avg Price (R$)', format='%.2f'),
                    'avg_review_score': st.column_config.NumberColumn('Avg Review Score', format='%.2f'),
                    'orders': st.column_config.NumberColumn('Orders', format='%d'),
                })
    
   