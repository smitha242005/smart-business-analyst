import pandas as pd
import numpy as np

def clean_data(filepath):
    # Read file based on extension
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        df = pd.read_excel(filepath)
    else:
        raise ValueError("Unsupported file format. Please upload CSV or Excel.")

    # Convert column names to lowercase and strip spaces
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')

    # Auto detect sales and profit columns
    possible_sales = ['sales', 'revenue', 'amount', 'total_sales', 'sale']
    possible_profit = ['profit', 'net_profit', 'earnings', 'income']
    possible_date = ['date', 'order_date', 'transaction_date', 'month']
    possible_region = ['region', 'area', 'location', 'zone']
    possible_category = ['category', 'product_category', 'type', 'segment']

    df = auto_rename_column(df, possible_sales, 'sales')
    df = auto_rename_column(df, possible_profit, 'profit')
    df = auto_rename_column(df, possible_date, 'date')
    df = auto_rename_column(df, possible_region, 'region')
    df = auto_rename_column(df, possible_category, 'category')

    # Drop rows where sales or profit is missing
    if 'sales' in df.columns:
        df = df.dropna(subset=['sales'])
    if 'profit' in df.columns:
        df = df.dropna(subset=['profit'])

    # Fill remaining missing values
    df = df.fillna(method='ffill').fillna(0)

    # Convert date column if exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year

    # Convert sales and profit to numeric
    if 'sales' in df.columns:
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
    if 'profit' in df.columns:
        df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)

    print(f"✅ Data cleaned successfully! Shape: {df.shape}")
    return df

def auto_rename_column(df, possible_names, target_name):
    for col in df.columns:
        if col in possible_names:
            df = df.rename(columns={col: target_name})
            return df
    return df