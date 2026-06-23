# E-Commerce Sales & Forecast Dashboard

An interactive Streamlit dashboard for exploring sales trends, product performance, customer behavior, and a short-term revenue forecast, built on the Brazilian Olist e-commerce dataset.

## Screenshot

TODO: add a screenshot of the live dashboard once deployed.

## Live Demo

TODO: add the Streamlit Cloud URL once deployed.

## Dashboard Pages

- **Overview** - revenue, orders, AOV and unique customer KPIs, monthly revenue trend, top categories, orders by day of week
- **Products** - revenue by category, price vs review score, top and bottom performing categories
- **Customers** - new vs returning customers, monthly customer acquisition, order status breakdown, revenue and delivery time by state
- **Forecast** - 3-month revenue forecast based on a Ridge regression model trained on historical monthly revenue

## Business Questions This Dashboard Answers

- How is monthly revenue trending, and how many orders and unique customers does that represent?
- Which product categories generate the most (and least) revenue?
- Is there a relationship between a category's average price and its average customer review score?
- What share of customers are repeat buyers vs new, and how fast is the customer base growing month over month?
- Which states generate the most revenue, and how does delivery speed vary by region?
- Based on recent trends, what revenue can be expected over the next 3 months?

## Forecasting Approach

Monthly revenue is aggregated into a time series, then 3 lag features (revenue from 1, 2 and 3 months ago) are used to predict the next month. The train/test split is time-based (first 80% of months for training, last 20% for testing) rather than random, since a random split would leak future information into training. LinearRegression and Ridge are compared by MAE on the test set - Ridge performed better after scaling the features with StandardScaler, and was selected as the final model. Full details, including data exploration and model evaluation, are in `notebooks/eda.ipynb`.

## Tech Stack

- **Python** - data processing
- **pandas** - data loading, merging, aggregation
- **Plotly Express** - interactive charts
- **Streamlit** - dashboard framework
- **scikit-learn** - Ridge / LinearRegression forecasting model
- **joblib** - model serialization

## How to Run Locally

```bash
git clone https://github.com/yaroslav-hezei/ecommerce-dashboard.git
cd ecommerce-dashboard
pip install -r requirements.txt
streamlit run Overview.py
```

## Dataset

Brazilian E-Commerce Public Dataset by Olist
Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
License: CC BY-NC-SA 4.0 - see `data/README.md` for details on which files are used.