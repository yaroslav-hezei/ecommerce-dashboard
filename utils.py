import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import streamlit as st


def read_data(path : Path) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        # Return None instead of raising so load_data() can decide how to handle
        # each missing file individually rather than aborting the entire merge chain.
        print(f"File not found: {path}")
        return None
    print(f"\n--- {path.name} ---\n")
    return df

# @st.cache_data serializes the returned DataFrame to bytes and stores it in
# Streamlit's cache, so the six CSV reads and all merges run only once per
# session — not on every widget interaction or page re-render.
@st.cache_data
def load_data() -> pd.DataFrame:
    # Anchor paths to this file's directory so the app works regardless of
    # where the user launches Streamlit from (cwd is not guaranteed to be the
    # project root when run via `streamlit run` from another directory).
    DATA_DIR = Path(__file__).parent / "data"

    #1
    orders = read_data(DATA_DIR / "olist_orders_dataset.csv")
    #2
    order_items = read_data(DATA_DIR / "olist_order_items_dataset.csv")
    #3
    products = read_data(DATA_DIR / "olist_products_dataset.csv")
    #4
    customers = read_data(DATA_DIR / "olist_customers_dataset.csv")
    #5
    category_translation = read_data(DATA_DIR / "product_category_name_translation.csv")
    #6
    reviews = read_data(DATA_DIR / "olist_order_reviews_dataset.csv")


    df = orders.merge(order_items, on = 'order_id', how = 'left')
    df = df.merge(products, on='product_id', how='left')
    df = df.merge(category_translation, on='product_category_name', how='left')
    df = df.merge(customers, on='customer_id', how='left')
    df = df.merge(reviews, on='order_id', how='left')

    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    # Cast Period to str so the column works as a plain groupby/filter key in
    # widgets and plotly — Period objects aren't JSON-serialisable and cause
    # errors in several Streamlit components.
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M').astype('str')

    return df


# @st.cache_resource is used here instead of @st.cache_data because the model
# and scaler are non-serialisable objects (sklearn estimators with internal C
# state). cache_resource stores them as live Python objects shared across
# sessions, whereas cache_data would try to pickle/unpickle them on every run.
@st.cache_resource
def load_model() -> tuple[Ridge | LinearRegression, StandardScaler]:
    # Same __file__-relative anchor as load_data() — keeps model paths correct
    # regardless of the working directory at launch time.
    MODELS_DIR = Path(__file__).parent / "models"

    model = joblib.load(MODELS_DIR / "best_model.pkl")
    scaler = joblib.load(MODELS_DIR / "scaler.pkl")

    return model,scaler


# Kept separate from load_data() so pages that need all statuses (e.g. a
# cancellation analysis) can still access the full DataFrame without reloading
# it. Filtering at the call site avoids baking an assumption about "delivered"
# into the shared cached dataset.
def filter_delivered(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['order_status'] == 'delivered']
    return df
