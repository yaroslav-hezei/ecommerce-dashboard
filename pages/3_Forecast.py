import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_data,filter_delivered,load_model


st.set_page_config(page_title='Sales Forecast', 
                   page_icon= '🔮', 
                   layout= 'wide',
                   initial_sidebar_state='expanded',
                   menu_items={
                       'Get help' : 'https://github.com/yaroslav-hezei/ecommerce-dashboard',
                       'Report a bug' : 'https://github.com/yaroslav-hezei/ecommerce-dashboard/issues'
                   })

st.title("Sales Forecast")
st.info(
    "This forecast estimates total revenue for the next 3 months based on recent "
    "monthly sales trends. It's a simple statistical model — it doesn't account for "
    "promotions, holidays, or other one-off events. Treat it as a directional signal, "
    "not an exact prediction."
    )

df = load_data()
df = filter_delivered(df)
model, scaler = load_model()


# Step 1: historical monthly revenue — same logic as app.py. No shift here:
# shift() builds training features (lag_1..3 per row), but we just need the raw series
# to pull the last known values from.
monthly_revenue = df.groupby('month')['price'].sum().reset_index()
monthly_revenue = monthly_revenue.sort_values('month').reset_index(drop=True)

last_month = monthly_revenue['month'].iloc[-1]
history = monthly_revenue['price'].tolist()  # growing list — each prediction gets appended

forecast_prices = []
forecast_months = []

# Steps 2-4: one model call per future month. Each prediction becomes the next lag_1,
# pushing lag_2/lag_3 one step back — this is what "recursive" means here.
for step in range(3):
    lag_1, lag_2, lag_3 = history[-1], history[-2], history[-3]

    # DataFrame with matching column names — scaler/model were fit on a DataFrame
    # with these exact names, a bare list/array would risk silent feature-order mismatches.
    features = pd.DataFrame({'lag_1': [lag_1], 'lag_2': [lag_2], 'lag_3': [lag_3]})
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]

    history.append(prediction)
    forecast_prices.append(prediction)
    forecast_months.append(str(pd.Period(last_month, freq='M') + step + 1))


historical = monthly_revenue.copy()
historical['type'] = 'Historical'

forecast_df = pd.DataFrame({
    'month': forecast_months,
    'price': forecast_prices,
    'type': 'Forecast'
})

# Duplicate the last historical point into the forecast series so the dashed
# line starts exactly where the solid line ends, instead of a visual gap.
bridge = historical.iloc[[-1]].copy()
bridge['type'] = 'Forecast'
forecast_df = pd.concat([bridge, forecast_df], ignore_index=True)

combined = pd.concat([historical, forecast_df], ignore_index=True)

fig = px.line(
    combined,
    x='month',
    y='price',
    color='type',
    title='Monthly Revenue — Historical & 3-Month Forecast',
    labels={'month': 'Month', 'price': 'Revenue (R$)', 'type': ''}
)

# px.line gives both traces solid lines by default — dash only the forecast one.
fig.for_each_trace(lambda t: t.update(line=dict(dash='dash')) if t.name == 'Forecast' else None)

with st.container(border=True):
    st.plotly_chart(fig, use_container_width=True)


# MAE from notebook Section 6 — hardcoded since the model isn't retrained at runtime.
mae_linear = 118917.48
mae_ridge = 107988.72
selected_mae = mae_ridge  # Ridge was selected as best_model

col1, col2 = st.columns(2)
col1.metric(label='Predicted Revenue (Next Month)', value=f"R$ {forecast_prices[0]:,.0f}", border=True)
col2.metric(label='Model MAE', value=f"R$ {selected_mae:,.0f}", border=True)

comparison_table = pd.DataFrame({
    'Model': ['LinearRegression', 'Ridge'],
    'MAE (R$)': [mae_linear, mae_ridge]
})

with st.container(border=True):
    st.dataframe(
        comparison_table,
        use_container_width=True,
        column_config={'MAE (R$)': st.column_config.NumberColumn('MAE (R$)', format='%.2f')}
    )
st.caption(
    "Limitations: the model is trained on a small dataset (~25 monthly data points), "
    "doesn't account for external factors like holidays or promotions, and accuracy "
    "decreases for predictions further into the future. Treat this forecast as "
    "indicative, not a guaranteed outcome."
)