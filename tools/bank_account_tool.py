from langchain.tools import tool
import re

@tool
def create_bank_account(name: str, second_name: str, id_number: str) -> str:
    """
    Create a bank account for a customer.
    
    Args:
        name: Customer's first name
        second_name: Customer's last name  
        id_number: Customer's ID number
        
    Returns:
        str: Account creation result
    """
    # Validate inputs
    if not name or not name.strip():
        return "Error: First name is required"
    
    if not second_name or not second_name.strip():
        return "Error: Last name is required"
    
    if not id_number or not id_number.strip():
        return "Error: ID number is required"
    
    # Basic validation
    name = name.strip()
    second_name = second_name.strip()
    id_number = id_number.strip()
    
    # Validate name contains only letters
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return "Error: First name should contain only letters"
    
    if not re.match(r'^[a-zA-Z\s]+$', second_name):
        return "Error: Last name should contain only letters"
    
    # Validate ID number (basic check - should be numeric and reasonable length)
    if not re.match(r'^\d{6,12}$', id_number):
        return "Error: ID number should be 6-12 digits"
    
    # If all validations pass, create account
    account_number = f"ACC{id_number[-6:]}{len(name):02d}"
    
    return f"✅ Bank account created successfully!\nAccount Number: {account_number}\nCustomer: {name} {second_name}\nID: {id_number}"