# Data

This project uses the Brazilian E-Commerce Public Dataset by Olist.

## Dataset

Brazilian E-Commerce Public Dataset by Olist
Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
License: CC BY-NC-SA 4.0 (Attribution, NonCommercial, ShareAlike)

## Files used by this app

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_products_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `product_category_name_translation.csv`

The Kaggle archive also includes `olist_order_payments_dataset.csv`, `olist_sellers_dataset.csv` and `olist_geolocation_dataset.csv` - these aren't used by `utils.py` and can be left out.

## Why the data is committed to this repo

Streamlit Community Cloud deploys straight from the connected GitHub repository - there's no separate storage for data files outside of git. The files above are well under 100 MB combined, so they're committed directly here instead of being hosted externally.

If you clone this repo, the data is already included - no manual download needed.