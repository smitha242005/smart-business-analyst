import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pickle
import os

def predict_sales(df):
    # Build features
    feature_cols = []

    if 'month' in df.columns:
        feature_cols.append('month')
    if 'year' in df.columns:
        feature_cols.append('year')
    if 'region' in df.columns:
        df['region_encoded'] = pd.factorize(df['region'])[0]
        feature_cols.append('region_encoded')
    if 'category' in df.columns:
        df['category_encoded'] = pd.factorize(df['category'])[0]
        feature_cols.append('category_encoded')
    if 'profit' in df.columns:
        feature_cols.append('profit')

    if len(feature_cols) == 0 or 'sales' not in df.columns:
        return dummy_results()

    X = df[feature_cols].fillna(0)
    y = df['sales']

    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_score = r2_score(y_test, lr.predict(X_test))

    # Train Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_score = r2_score(y_test, rf.predict(X_test))

    # Pick best model
    if rf_score >= lr_score:
        best_model = rf
        best_score = rf_score
        model_name = "Random Forest"
    else:
        best_model = lr
        best_score = lr_score
        model_name = "Linear Regression"

    # Save model
    os.makedirs('model', exist_ok=True)
    with open('model/sales_prediction.pkl', 'wb') as f:
        pickle.dump(best_model, f)

    # Predictions
    y_pred = best_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Predict next month sales
    last_row = X.iloc[-1].copy()
    if 'month' in feature_cols:
        last_row['month'] = (last_row['month'] % 12) + 1
    next_pred = best_model.predict([last_row.values])[0]

    # Predict next month profit
    predicted_profit = next_pred * 0.15

    # Chart data - monthly sales trend
    chart_data = get_chart_data(df)

    print(f"✅ Best Model: {model_name} | Accuracy: {round(best_score * 100, 2)}%")

    return {
        'predicted_sales': round(float(next_pred), 2),
        'predicted_profit': round(float(predicted_profit), 2),
        'accuracy': round(float(best_score * 100), 2),
        'mae': round(float(mae), 2),
        'rmse': round(float(rmse), 2),
        'model_name': model_name,
        'chart_data': chart_data
    }

def get_chart_data(df):
    chart_data = {}

    # Monthly sales trend
    if 'month' in df.columns and 'sales' in df.columns:
        monthly = df.groupby('month')['sales'].sum().reset_index()
        chart_data['monthly_labels'] = monthly['month'].tolist()
        chart_data['monthly_sales'] = monthly['sales'].round(2).tolist()

    # Region wise sales
    if 'region' in df.columns and 'sales' in df.columns:
        region = df.groupby('region')['sales'].sum().reset_index()
        chart_data['region_labels'] = region['region'].tolist()
        chart_data['region_sales'] = region['sales'].round(2).tolist()

    # Category wise profit
    if 'category' in df.columns and 'profit' in df.columns:
        category = df.groupby('category')['profit'].sum().reset_index()
        chart_data['category_labels'] = category['category'].tolist()
        chart_data['category_profit'] = category['profit'].round(2).tolist()

    return chart_data

def dummy_results():
    return {
        'predicted_sales': 0,
        'predicted_profit': 0,
        'accuracy': 0,
        'mae': 0,
        'rmse': 0,
        'model_name': 'N/A',
        'chart_data': {}
    }