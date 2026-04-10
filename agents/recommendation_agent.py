def get_recommendations(results):
    recommendations = []
    
    predicted_sales = results['predicted_sales']
    predicted_profit = results['predicted_profit']
    accuracy = results['accuracy']
    chart_data = results['chart_data']

    # Sales based recommendations
    if predicted_sales > 10000:
        recommendations.append("🚀 High sales predicted next month — increase stock levels to meet demand.")
    elif predicted_sales > 5000:
        recommendations.append("📈 Moderate sales expected — maintain current inventory levels.")
    else:
        recommendations.append("⚠️ Low sales predicted — consider running promotions or discounts.")

    # Profit based recommendations
    if predicted_profit > 2000:
        recommendations.append("💰 Strong profit margin expected — good time to invest in marketing.")
    elif predicted_profit > 500:
        recommendations.append("📊 Average profit predicted — review pricing strategy to improve margins.")
    else:
        recommendations.append("🔴 Low profit predicted — reduce unnecessary operational costs.")

    # Region based recommendations
    if 'region_labels' in chart_data and 'region_sales' in chart_data:
        regions = chart_data['region_labels']
        sales = chart_data['region_sales']

        if regions and sales:
            max_idx = sales.index(max(sales))
            min_idx = sales.index(min(sales))
            recommendations.append(
                f"🌟 {regions[max_idx]} region has the highest sales — focus more resources here."
            )
            recommendations.append(
                f"📉 {regions[min_idx]} region has the lowest sales — investigate and improve marketing."
            )

    # Category based recommendations
    if 'category_labels' in chart_data and 'category_profit' in chart_data:
        categories = chart_data['category_labels']
        profits = chart_data['category_profit']

        if categories and profits:
            max_idx = profits.index(max(profits))
            min_idx = profits.index(min(profits))
            recommendations.append(
                f"✅ {categories[max_idx]} category is most profitable — expand this product line."
            )
            recommendations.append(
                f"❌ {categories[min_idx]} category has lowest profit — consider discontinuing or repricing."
            )

    # Monthly trend recommendations
    if 'monthly_sales' in chart_data:
        monthly_sales = chart_data['monthly_sales']
        if monthly_sales:
            min_month_idx = monthly_sales.index(min(monthly_sales))
            month_names = [
                "January", "February", "March", "April",
                "May", "June", "July", "August",
                "September", "October", "November", "December"
            ]
            weak_month = month_names[min_month_idx] if min_month_idx < 12 else "Unknown"
            recommendations.append(
                f"📅 Sales are weakest in {weak_month} — plan special offers during this period."
            )

    # Model accuracy recommendations
    if accuracy >= 90:
        recommendations.append("🎯 Model accuracy is excellent — predictions are highly reliable.")
    elif accuracy >= 75:
        recommendations.append("📌 Model accuracy is good — predictions can be used for planning.")
    else:
        recommendations.append("⚠️ Model accuracy is low — collect more data for better predictions.")

    return recommendations