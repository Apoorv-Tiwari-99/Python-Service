import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os

def get_user_expenses(user_id):
    """Fetch user expenses from the backend API"""
    try:
        backend_url = os.getenv('BACKEND_URL')
        response = requests.get(f"{backend_url}/api/expenses", params={'userId': user_id})
        
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            print(f"Error fetching expenses: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception fetching expenses: {e}")
        return []

def analyze_spending(expenses):
    """Analyze spending patterns and generate suggestions"""
    if not expenses:
        return {"suggestions": [], "summary": {}}
    
    # Convert to DataFrame
    df = pd.DataFrame(expenses)
    
    # Convert date strings to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Get current date and calculate date ranges
    current_date = datetime.now()
    thirty_days_ago = current_date - timedelta(days=30)
    sixty_days_ago = current_date - timedelta(days=60)
    
    # Filter data for last 30 and 60 days
    last_30_days = df[df['date'] >= thirty_days_ago]
    previous_30_days = df[(df['date'] >= sixty_days_ago) & (df['date'] < thirty_days_ago)]
    
    # Calculate total spending
    total_current = last_30_days['amount'].sum()
    total_previous = previous_30_days['amount'].sum()
    
    # Calculate spending by category
    current_by_category = last_30_days.groupby('category')['amount'].sum().to_dict()
    previous_by_category = previous_30_days.groupby('category')['amount'].sum().to_dict()
    
    # Generate suggestions
    suggestions = []
    
    # Overall spending comparison
    if total_previous > 0:
        spending_change = ((total_current - total_previous) / total_previous) * 100
        if spending_change > 20:
            suggestions.append({
                "type": "warning",
                "message": f"Your overall spending increased by {spending_change:.1f}% compared to the previous month."
            })
        elif spending_change < -15:
            suggestions.append({
                "type": "positive",
                "message": f"Great job! Your overall spending decreased by {abs(spending_change):.1f}% compared to the previous month."
            })
    
    # Category-wise analysis
    all_categories = set(current_by_category.keys()) | set(previous_by_category.keys())
    
    for category in all_categories:
        current_spend = current_by_category.get(category, 0)
        previous_spend = previous_by_category.get(category, 0)
        
        # Skip if no previous spending for comparison
        if previous_spend == 0:
            if current_spend > 0:
                suggestions.append({
                    "type": "info",
                    "message": f"You started spending on {category} this month (₹{current_spend:.2f})."
                })
            continue
        
        # Calculate percentage change
        if previous_spend > 0:
            change_percent = ((current_spend - previous_spend) / previous_spend) * 100
            
            if change_percent > 50 and current_spend > 1000:  # Significant increase
                suggestions.append({
                    "type": "warning",
                    "message": f"Your {category} expenses increased significantly by {change_percent:.1f}% compared to last month."
                })
            elif change_percent < -30:  # Significant decrease
                suggestions.append({
                    "type": "positive",
                    "message": f"Great job reducing {category} expenses by {abs(change_percent):.1f}% compared to last month."
                })
        
        # High spending alert
        if current_spend > 5000:  # Arbitrary threshold
            suggestions.append({
                "type": "warning",
                "message": f"You're spending a lot on {category} (₹{current_spend:.2f}). Consider looking for ways to reduce this expense."
            })
    
    # Check for unusual spending patterns
    daily_spending = last_30_days.groupby(last_30_days['date'].dt.date)['amount'].sum()
    avg_daily_spend = daily_spending.mean()
    std_daily_spend = daily_spending.std()
    
    if std_daily_spend > 0:
        # Find days with unusually high spending
        unusual_days = daily_spending[daily_spending > avg_daily_spend + (2 * std_daily_spend)]
        
        for day, amount in unusual_days.items():
            day_expenses = last_30_days[last_30_days['date'].dt.date == day]
            top_category = day_expenses.groupby('category')['amount'].sum().idxmax()
            
            suggestions.append({
                "type": "info",
                "message": f"Unusually high spending on {day.strftime('%Y-%m-%d')} (₹{amount:.2f}), mostly on {top_category}."
            })
    
    # If no specific suggestions, provide general advice
    if not suggestions:
        suggestions.append({
            "type": "info",
            "message": "Your spending patterns look normal. Keep tracking your expenses to maintain good financial health."
        })
    
    # Prepare summary
    summary = {
        "total_current": total_current,
        "total_previous": total_previous,
        "spending_change": ((total_current - total_previous) / total_previous * 100) if total_previous > 0 else 0,
        "top_category": max(current_by_category.items(), key=lambda x: x[1])[0] if current_by_category else "No spending",
        "category_breakdown": current_by_category
    }
    
    return {
        "suggestions": suggestions[:5],  # Return top 5 suggestions
        "summary": summary
    }

def generate_budget_recommendations(expenses, current_budgets=None):
    """Generate budget recommendations based on spending patterns"""
    if not expenses:
        return {"recommendations": []}
    
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    
    # Get last 3 months of data
    three_months_ago = datetime.now() - timedelta(days=90)
    recent_data = df[df['date'] >= three_months_ago]
    
    if recent_data.empty:
        return {"recommendations": []}
    
    # Calculate average monthly spending by category
    recent_data['month'] = recent_data['date'].dt.to_period('M')
    monthly_spending = recent_data.groupby(['category', 'month'])['amount'].sum().reset_index()
    avg_spending = monthly_spending.groupby('category')['amount'].mean().to_dict()
    
    recommendations = []
    
    for category, avg_amount in avg_spending.items():
        # Add buffer (10%) to average spending for budget recommendation
        recommended_budget = avg_amount * 1.1
        
        # Check if user already has a budget for this category
        current_budget = None
        if current_budgets:
            for budget in current_budgets:
                if budget.get('category') == category:
                    current_budget = budget.get('monthlyLimit')
                    break
        
        if current_budget:
            # Compare current budget with recommendation
            difference = ((recommended_budget - current_budget) / current_budget) * 100
            
            if abs(difference) > 20:  # Significant difference
                action = "increase" if difference > 0 else "decrease"
                recommendations.append({
                    "category": category,
                    "current_budget": current_budget,
                    "recommended_budget": recommended_budget,
                    "action": action,
                    "message": f"Consider {action}ing your {category} budget from ₹{current_budget:.2f} to ₹{recommended_budget:.2f} based on your spending patterns."
                })
        else:
            # No existing budget, suggest creating one
            recommendations.append({
                "category": category,
                "recommended_budget": recommended_budget,
                "action": "create",
                "message": f"Consider setting a budget of ₹{recommended_budget:.2f} for {category} based on your average spending."
            })
    
    return {"recommendations": recommendations}