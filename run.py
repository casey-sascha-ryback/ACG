"""
Run script for Cybersecurity Toolkit

This script provides an easy way to run the application.
It sets up proper imports and starts the application with the Flask development server.
"""

import os
import sys
import argparse
import importlib.util

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run the Cybersecurity Toolkit')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the application on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the application on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    return parser.parse_args()

def check_dependencies():
    """Check if required dependencies are installed and suggest installation if missing"""
    required_packages = [
        'flask', 'flask_session', 'flask_sqlalchemy', 
        'cryptography', 'email_validator', 'requests',
        'numpy', 'sklearn'
    ]
    
    missing_packages = []
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("Warning: The following required packages are missing:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nTo install missing dependencies, run:")
        print("  pip install -r requirements.txt")
        
        # Ask if user wants to continue anyway
        response = input("\nDo you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

def load_env_file():
    """Load environment variables from .env file if available"""
    try:
        dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(dotenv_path):
            # Try to use python-dotenv if available
            try:
                from dotenv import load_dotenv
                load_dotenv(dotenv_path)
                print("Environment variables loaded from .env file")
            except ImportError:
                # Manual parsing if python-dotenv is not available
                with open(dotenv_path) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"\'')
                print("Environment variables loaded from .env file (manual parsing)")
        else:
            print("No .env file found, using environment defaults")
    except Exception as e:
        print(f"Warning: Failed to load environment variables: {e}")

def run_application():
    """Run the Cybersecurity Toolkit application"""
    args = parse_arguments()
    
    # Add project root to Python path to ensure imports work
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Load environment variables
    load_env_file()
    
    # Check dependencies
    check_dependencies()
    
    # Import the application (after environment setup)
    from app import app
    
    # Confirm application is starting
    port = args.port
    host = args.host
    debug = args.debug
    
    print(f"Starting Cybersecurity Toolkit with MVC Architecture")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug mode: {'enabled' if debug else 'disabled'}")
    print(f"Project root: {project_root}")
    print("Application URL: http://localhost:{} (if running locally)".format(port))
    print("--------------------------------------------------")
    
    # Run the application
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_application()