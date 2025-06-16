# Cybersecurity Toolkit Structure


## Core Application Entry Points
```
/
├── main.py                    # Primary entry point - imports Flask app from app.py
├── app.py                     # Main Flask application with all routes and imports
└── run.py                     # Can be used to run the application instead of main.py
```

## Business Logic (Models/Tools)
```
/tools/                        # Primary business logic directory
├── password_analyzer.py       # Password strength analysis - ACTIVELY USED
├── file_integrity.py          # File checksum and integrity checking - ACTIVELY USED
└── encryption_tool.py         # Encryption/decryption functionality - ACTIVELY USED

/models/                       # Supporting models directory
├── leakcheck_integration.py   # LeakCheck API integration - ACTIVELY USED

/
├── models.py                  # Password strength ML model implementation (testing)
├── simple_encryption.py       # Portable encryption fallback (testing)
└── password_model.pkl         # Trained scikit-learn model file - ACTIVELY USED (It will be created once it's not existing during intial program execution)
```

## User Interface (Templates & Static Assets)
```
/templates/                    # HTML templates - ALL ACTIVELY USED
├── base.html                  # Base template with navigation
├── index.html                 # Home page
├── about.html                 # About page
├── password_analyzer.html     # Password analyzer interface
├── dark_web_monitor.html      # Dark web monitor interface
├── file_integrity.html        # File integrity checker interface
├── encryption_tool.html       # Encryption tool interface
└── error.html                 # Error page template

/static/                       # Static assets - ALL ACTIVELY USED (except for images)
├── css/
│   └── styles.css             # Main stylesheet
├── js/
│   ├── password_strength.js   # Password analyzer JavaScript
│   ├── dark_web.js            # Dark web monitor JavaScript
│   ├── file_integrity.js      # File integrity JavaScript
│   └── encryption.js          # Encryption tool JavaScript
└── images/                    # Image assets directory (no images)
```

## Machine Learning Implementation Analysis

### Actively Used Libraries:
1. **scikit-learn** (Primary ML implementation):
   - `models.py`: Uses CountVectorizer and RandomForestClassifier
   - `password_model.pkl`: Serialized scikit-learn model
   - `tools/password_analyzer.py`: Loads and uses the scikit-learn model

## Execution Flow Verification

1. **Application Start**: `main.py` or `run.py` → imports `app` from `app.py`
2. **Route Handling**: `app.py` contains all route definitions
3. **Business Logic**: Routes import functions from:
   - `tools/password_analyzer.py` (analyze_password, load_password_model)
   - `models/leakcheck_integration.py` (check_breach)
   - `tools/file_integrity.py` (calculate_checksum, verify_checksum)
   - `tools/encryption_tool.py` (encrypt_text, decrypt_text, available_algorithms)
4. **Templates**: Flask renders HTML templates from `/templates/`
5. **Static Assets**: Served from `/static/`


## Summary

The application primarily operates as a monolithic Flask app in `app.py` that imports specific functions from the `/tools/` directory for business logic, uses `/templates/` for UI, and `/static/` for assets. The MVC structure exists but the current execution path uses a simplified architecture with all routes in the main app file.