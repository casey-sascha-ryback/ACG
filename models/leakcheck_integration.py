"""
LeakCheck API Integration
This module provides direct integration with the LeakCheck API for breach checking
"""

from leakcheck import LeakCheckAPI_Public
import logging
import json

def check_breach(email):
    """
    Check if an email has been involved in any data breaches using LeakCheck API
    
    Args:
        email (str): The email to check
        
    Returns:
        list: List of standardized breach data
    """
    try:
        # Initialize the LeakCheck public API
        api = LeakCheckAPI_Public()
        
        # Make the API request
        logging.info(f"Checking breaches for email: {email[:3]}***")
        response = api.lookup(query=email)
        
        # If this is a test email, use demo data
        if email.lower() in ['test@example.com', 'demo@example.com', 'breach@example.com']:
            return get_demo_breaches()
            
        # Process the breach data if found
        if response and isinstance(response, dict) and response.get('success'):
            found_count = response.get('found', 0)
            logging.info(f"LeakCheck found {found_count} breaches")
            
            # If no breaches found, return empty list
            if found_count == 0 or not response.get('sources'):
                return []
                
            # Process the sources into standardized breach format
            breaches = []
            
            # Strictly follow the LeakCheck API JSON format
            # Include the total count only once in the first breach
            for idx, source in enumerate(response.get('sources', [])[:20]):  # Limit to 20 sources
                breach = {
                    'Name': source.get('name', 'Unknown Source'),
                    'Title': source.get('name', 'Unknown Source'),
                    'Domain': source.get('name', 'unknown').lower().replace(' ', '').replace('.', ''),
                    'BreachDate': source.get('date', '2023-01-01'),
                    'AddedDate': '2023-01-01',
                    'Description': f"Your data was found in the {source.get('name', 'Unknown')} breach.",
                    'DataClasses': get_data_classes(response),
                    'LogoPath': 'https://haveibeenpwned.com/Content/Images/PwnedLogos/Breach.png',
                    'PwnCount': source.get('entries', found_count),
                    'IsVerified': True,
                    'found': found_count  # Add the total count from the API response
                }
                breaches.append(breach)
                
            return breaches
        else:
            logging.warning(f"LeakCheck response not successful: {response}")
            return []
            
    except Exception as e:
        logging.error(f"Error checking LeakCheck API: {str(e)}")
        return []
        
def get_data_classes(response):
    """Extract data classes from LeakCheck response"""
    data_classes = []
    
    if 'fields' in response and response['fields']:
        for field in response['fields']:
            if field == 'username': data_classes.append('Usernames')
            elif field == 'email': data_classes.append('Email addresses')
            elif field == 'password': data_classes.append('Passwords')
            elif field in ['first_name', 'last_name', 'name']: data_classes.append('Names')
            elif field == 'phone': data_classes.append('Phone numbers')
            elif field == 'address': data_classes.append('Addresses')
            elif field in ['ip', 'ip1', 'ip2']: data_classes.append('IP addresses')
            else: data_classes.append(field.capitalize())
    else:
        # Default data class if none specified
        data_classes = ['Email addresses']
        
    return data_classes
    
def get_demo_breaches():
    """Return demo breach data for test emails"""
    # Total breach count for the demo
    total_found = 6300000
    
    return [
        {
            'Name': 'DemoBreachData',
            'Title': 'Demo Breach',
            'Domain': 'demo-service.com',
            'BreachDate': '2023-01-15',
            'AddedDate': '2023-02-01',
            'Description': 'This is a simulated breach for educational purposes. In a real scenario, this would contain information about an actual data breach.',
            'DataClasses': ['Email addresses', 'Passwords', 'Names', 'IP addresses'],
            'LogoPath': 'https://haveibeenpwned.com/Content/Images/PwnedLogos/Adobe.png',
            'PwnCount': 5430000,
            'IsVerified': True,
            'demo': True,
            'found': total_found
        },
        {
            'Name': 'AnotherDemoBreachData',
            'Title': 'Another Demo Breach',
            'Domain': 'another-demo.com',
            'BreachDate': '2022-11-20',
            'AddedDate': '2022-12-05',
            'Description': 'Another simulated breach for demonstration. This represents how multiple breaches would be displayed.',
            'DataClasses': ['Email addresses', 'Geographic locations', 'Phone numbers'],
            'LogoPath': 'https://haveibeenpwned.com/Content/Images/PwnedLogos/Yahoo.png',
            'PwnCount': 870000,
            'IsVerified': True,
            'demo': True,
            'found': total_found
        }
    ]