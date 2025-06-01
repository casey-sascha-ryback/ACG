"""
Cybersecurity Toolkit - Main Application Entry Point

This file follows the MVC (Model-View-Controller) architecture:
- Models: Located in the models/ directory (data and business logic)
- Views: Located in the templates/ directory (UI presentation logic)
- Controllers: using the app.py for request handling

This structure ensures the application is portable and can run in any IDE.
"""

# Import Flask app from app.py
# For now, keep importing from app.py to maintain functionality
# This can be refactored for any further development
from app import app

# This allows the application to be run directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
