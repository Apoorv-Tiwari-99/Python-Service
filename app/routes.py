from flask import Blueprint, request, jsonify
from app.utils import get_user_expenses, analyze_spending, generate_budget_recommendations
import requests
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Python Smart Suggestions API"
    })

@main_bp.route('/analyze/<user_id>', methods=['GET'])
def analyze_user_spending(user_id):
    """Analyze user spending and provide suggestions"""
    try:
        print(f"Received request for user: {user_id}")
        
        # Get user expenses
        backend_url = os.getenv('BACKEND_URL')
        print(f"Backend URL: {backend_url}")
        
        expenses = get_user_expenses(user_id)
        print(f"Retrieved {len(expenses)} expenses")
        
        if not expenses:
            return jsonify({
                "success": True,
                "data": {
                    "suggestions": [{
                        "type": "info",
                        "message": "No spending data available for analysis."
                    }],
                    "summary": {}
                }
            })
        
        # Analyze spending
        print("Analyzing spending patterns...")
        analysis = analyze_spending(expenses)
        print(f"Generated {len(analysis.get('suggestions', []))} suggestions")
        
        return jsonify({
            "success": True,
            "data": analysis
        })
        
    except Exception as e:
        print(f"Error in analyze_user_spending: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error analyzing spending: {str(e)}"
        }), 500

@main_bp.route('/budget-recommendations/<user_id>', methods=['GET'])
def get_budget_recommendations(user_id):
    """Get budget recommendations for a user"""
    try:
        # Get user expenses
        expenses = get_user_expenses(user_id)
        
        # Get current budgets
        backend_url = os.getenv('BACKEND_URL')
        budgets_response = requests.get(f"{backend_url}/api/budgets", params={'userId': user_id})
        
        current_budgets = []
        if budgets_response.status_code == 200:
            current_budgets = budgets_response.json().get('data', [])
        
        # Generate recommendations
        recommendations = generate_budget_recommendations(expenses, current_budgets)
        
        return jsonify({
            "success": True,
            "data": recommendations
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error generating budget recommendations: {str(e)}"
        }), 500

@main_bp.route('/full-analysis/<user_id>', methods=['GET'])
def get_full_analysis(user_id):
    """Get complete financial analysis for a user"""
    try:
        # Get user expenses
        expenses = get_user_expenses(user_id)
        
        # Analyze spending
        spending_analysis = analyze_spending(expenses)
        
        # Get budget recommendations
        backend_url = os.getenv('BACKEND_URL')
        budgets_response = requests.get(f"{backend_url}/api/budgets", params={'userId': user_id})
        
        current_budgets = []
        if budgets_response.status_code == 200:
            current_budgets = budgets_response.json().get('data', [])
        
        budget_recommendations = generate_budget_recommendations(expenses, current_budgets)
        
        # Combine results
        full_analysis = {
            "spending_analysis": spending_analysis,
            "budget_recommendations": budget_recommendations
        }
        
        return jsonify({
            "success": True,
            "data": full_analysis
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error performing full analysis: {str(e)}"
        }), 500