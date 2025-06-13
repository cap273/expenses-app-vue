#!/usr/bin/env python3
"""
Test script to validate manual expense creation and identify issues with:
1. New expenses not updating category averages 
2. Merchant/vendor name storage and display issues
"""

import requests
import json
from datetime import datetime, date

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_manual_expense_creation():
    """Test creating a manual expense and validate it appears correctly"""
    print("Testing manual expense creation...")
    
    # First, get available scopes
    scopes_response = requests.get(f"{BASE_URL}/api/get_scopes")
    if not scopes_response.ok:
        print(f"Error getting scopes: {scopes_response.status_code}")
        return False
    
    scopes = scopes_response.json()
    if not scopes.get('success') or not scopes.get('scopes'):
        print("No scopes available")
        return False
    
    scope_id = scopes['scopes'][0]['id']
    print(f"Using scope ID: {scope_id}")
    
    # Create a new manual expense
    test_expense = {
        "expenses": [
            {
                "scope": scope_id,
                "day": datetime.now().day,
                "month": datetime.now().strftime("%B"),
                "year": datetime.now().year,
                "amount": "123.45",
                "category": "Groceries",
                "merchant": "Test Merchant Store",
                "notes": "Test manual expense"
            }
        ]
    }
    
    print(f"Creating expense: {test_expense}")
    
    # Submit the expense
    create_response = requests.post(
        f"{BASE_URL}/api/submit_expenses",
        json=test_expense,
        headers={'Content-Type': 'application/json'}
    )
    
    if not create_response.ok:
        print(f"Error creating expense: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False
    
    result = create_response.json()
    if not result.get('success'):
        print(f"Failed to create expense: {result.get('error')}")
        return False
    
    print(f"Expense created successfully: {result.get('message')}")
    return True

def test_category_averages_update():
    """Test if new expenses update category averages"""
    print("\nTesting category averages update...")
    
    # Get category averages before
    averages_response = requests.get(f"{BASE_URL}/api/get_category_averages")
    if not averages_response.ok:
        print(f"Error getting averages: {averages_response.status_code}")
        return False
    
    averages_before = averages_response.json()
    print(f"Averages before: {json.dumps(averages_before, indent=2)}")
    
    # Get category progress
    progress_response = requests.get(f"{BASE_URL}/api/get_category_progress")
    if not progress_response.ok:
        print(f"Error getting progress: {progress_response.status_code}")
        return False
    
    progress = progress_response.json()
    print(f"Category progress: {json.dumps(progress, indent=2)}")
    
    return True

def test_expense_editing():
    """Test editing an expense and check merchant name persistence"""
    print("\nTesting expense editing...")
    
    # Get existing expenses
    expenses_response = requests.get(f"{BASE_URL}/api/get_expenses")
    if not expenses_response.ok:
        print(f"Error getting expenses: {expenses_response.status_code}")
        return False
    
    expenses_data = expenses_response.json()
    if not expenses_data.get('success') or not expenses_data.get('expenses'):
        print("No expenses found")
        return False
    
    # Find a manual expense
    manual_expenses = [e for e in expenses_data['expenses'] if e.get('SourceType') == 'manual']
    if not manual_expenses:
        print("No manual expenses found")
        return False
    
    expense = manual_expenses[0]
    print(f"Original expense: {json.dumps(expense, indent=2)}")
    
    # Update the expense
    updated_expense = {
        "expenses": [
            {
                "ExpenseID": expense['ExpenseID'],
                "scope": expense['ScopeID'],
                "day": expense['Day'],
                "month": expense['Month'],
                "year": expense['Year'],
                "amount": str(expense['Amount']).replace('$', '').replace(',', ''),
                "category": expense['ExpenseCategory'],
                "merchant": expense.get('MerchantName', '') or "Updated Merchant Name",
                "notes": expense.get('AdditionalNotes', '') or "Updated notes"
            }
        ]
    }
    
    print(f"Updating expense to: {json.dumps(updated_expense, indent=2)}")
    
    # Submit the update
    update_response = requests.put(
        f"{BASE_URL}/api/update_expense",
        json=updated_expense,
        headers={'Content-Type': 'application/json'}
    )
    
    if not update_response.ok:
        print(f"Error updating expense: {update_response.status_code}")
        print(f"Response: {update_response.text}")
        return False
    
    result = update_response.json()
    if not result.get('success'):
        print(f"Failed to update expense: {result.get('error')}")
        return False
    
    print(f"Expense updated successfully: {result.get('message')}")
    
    # Get the updated expense to verify changes
    updated_expenses_response = requests.get(f"{BASE_URL}/api/get_expenses")
    if updated_expenses_response.ok:
        updated_expenses_data = updated_expenses_response.json()
        if updated_expenses_data.get('success'):
            updated_expense_obj = next(
                (e for e in updated_expenses_data['expenses'] if e['ExpenseID'] == expense['ExpenseID']),
                None
            )
            if updated_expense_obj:
                print(f"Updated expense: {json.dumps(updated_expense_obj, indent=2)}")
                
                # Check if merchant name was stored correctly
                if updated_expense_obj.get('MerchantName'):
                    print("✓ Merchant name stored correctly")
                else:
                    print("✗ Merchant name not stored or lost")
                    return False
            else:
                print("Could not find updated expense")
                return False
    
    return True

def main():
    """Run all tests"""
    print("Starting manual expense validation tests...")
    print("=" * 50)
    
    try:
        # Test 1: Create a manual expense
        if not test_manual_expense_creation():
            print("❌ Manual expense creation test failed")
            return
        
        # Test 2: Check category averages update
        if not test_category_averages_update():
            print("❌ Category averages update test failed")
            return
        
        # Test 3: Test expense editing and merchant name persistence
        if not test_expense_editing():
            print("❌ Expense editing test failed")
            return
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Make sure the Flask backend is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()