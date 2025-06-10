import re
import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import logging


# Password strength model class
class PasswordStrengthModel:
    """
    A model for predicting password strength using scikit-learn.
    This model uses character n-grams and length features to predict password strength.
    """

    def __init__(self):
        # Initialize the model components
        self.vectorizer = CountVectorizer(analyzer='char', ngram_range=(1, 3))
        self.classifier = LogisticRegression(solver='liblinear', max_iter=200)
        self.is_trained = False

    def train(self, passwords, strengths):
        """
        Train the model with example passwords and their strength ratings.
        
        Args:
            passwords (list): List of password strings
            strengths (list): List of strength ratings (0-4, where 0 is very weak, 4 is very strong)
        """
        # Extract character n-gram features
        X_chars = self.vectorizer.fit_transform(passwords)

        # Add password length as a feature
        length_feature = np.array([len(p) for p in passwords]).reshape(-1, 1)

        # Combine features
        X = np.hstack((X_chars.toarray(), length_feature))

        # Train the classifier
        self.classifier.fit(X, strengths)
        self.is_trained = True

    def predict(self, password):
        """
        Predict the strength of a password.
        
        Args:
            password (str): The password to evaluate
            
        Returns:
            int: Predicted strength (0-4)
        """
        # Check character composition requirements
        length = len(password)
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        # STRICT RULE: Passwords under 8 characters can never be strong
        if length < 8:
            if length < 4:
                return 0  # Very weak
            else:
                return 1  # Weak maximum for short passwords
        
        # STRICT RULE: For Strong (3) or Very Strong (4), must have ALL character types
        all_char_types = has_lowercase and has_uppercase and has_digit and has_special
        
        if not self.is_trained:
            # If model is not trained, use a simple heuristic
            return self._simple_strength_check(password)

        # Extract character n-gram features
        X_chars = self.vectorizer.transform([password])

        # Add password length as a feature
        length_feature = np.array([length]).reshape(-1, 1)

        # Combine features
        X = np.hstack((X_chars.toarray(), length_feature))

        # Predict strength
        prediction = self.classifier.predict(X)[0]
        
        # Apply strict character type requirements
        if prediction >= 3 and not all_char_types:
            # Downgrade to Moderate (2) if missing any character type
            prediction = 2
        
        return prediction

    def _simple_strength_check(self, password):
        """Simple heuristic for password strength if model isn't trained"""
        length = len(password)
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        # STRICT RULE: Passwords under 8 characters can never be strong
        if length < 8:
            if length < 4:
                return 0  # Very weak
            else:
                return 1  # Weak maximum for short passwords

        # STRICT RULE: For Strong (3) or Very Strong (4), must have ALL character types
        all_char_types = has_lowercase and has_uppercase and has_digit and has_special
        
        # Count criteria met (only for passwords 8+ characters)
        criteria_count = sum([
            has_lowercase, has_uppercase, has_digit, has_special
        ])

        # Map to strength score (0-4) for passwords 8+ characters
        if criteria_count <= 1:
            return 1  # Weak
        elif criteria_count == 2:
            return 2  # Moderate
        elif criteria_count == 3:
            return 2  # Moderate (missing one character type)
        elif all_char_types and length >= 12:
            return 4  # Very Strong (8+ chars with all types AND 12+ length)
        elif all_char_types:
            return 3  # Strong (8+ chars with all types)
        else:
            return 2  # Moderate (should not reach here, but safety)

    def save_model(self, filepath):
        """Save the trained model to a file"""
        with open(filepath, 'wb') as f:
            pickle.dump(
                {
                    'vectorizer': self.vectorizer,
                    'classifier': self.classifier,
                    'is_trained': self.is_trained
                }, f)
        return True

    def load_model(self, filepath):
        """Load a trained model from a file"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
                self.vectorizer = model_data['vectorizer']
                self.classifier = model_data['classifier']
                self.is_trained = model_data['is_trained']
            return True
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
            return False


def initialize_default_model():
    """Initialize and train a default password strength model"""
    # Create sample data for training with proper strength classifications
    passwords = [
        # Very weak passwords (0) - short, simple, repetitive
        "123",
        "abc",
        "111",
        "1234",
        "aaaa",
        "1111111",  # 7 chars, repetitive
        "abcdef",   # 6 chars
        "123456",   # common weak
        "password", # common weak
        "qwerty",   # common weak
        # Weak passwords (1) - under 8 chars or poor patterns
        "abc123",
        "letmein",
        "monkey",
        "12345678",  # 8 chars but all numbers
        "abcdefgh",  # 8 chars but all letters
        "PASSWORD",  # 8 chars but all caps
        "football",
        "iloveyou",
        # Moderate passwords (2) - 8+ chars with some complexity
        "starwars1",
        "baseball2",
        "password123",
        "superman1",
        "sunshine9",
        "Welcome1",
        "Passw0rd",
        "Computer1",
        # Strong passwords (3) - 8+ chars with good complexity
        "Qwerty123!",
        "Password123@",
        "Welcome123#",
        "Security2024$",
        "MyP@ssw0rd",
        "Ch@nge123",
        "Str0ng!Pass",
        "C0mplex#123",
        # Very strong passwords (4) - 12+ chars with high complexity
        "MyVeryStr0ng!P@ssw0rd",
        "Tr0ub4dor&3SecurePass",
        "P@$$w0rd123!Complex",
        "2Fa$PasswordSecure123",
        "p@s5W0rD!2FaStr0ng",
        "ComplexP@ssw0rd!2024",
        # Additional high-entropy strong passwords
        "wd+;V9%H",
        "cJ-H*4,{",
        "F+wQ8c*b",
        "E7/%n}-a",
        "N2n,L@T(",
        "x{;Q\"(8D",
        "k%cH}9Qq",
        "a;H_3Szv",
        "D)86BnR$",
        "jD7Kp9;Y",
        "Es)p3a;w",
        "RC(7XNd+",
        "u-}#2AE.",
        "c=uHJ{4T",
        "gyC3K@Dh",
        "a,BJ?9R.",
        "c[HZB6^7",
        "u&-e94T6",
        "w?X4J@8K",
        "y4`mzPrU",
        "P^8c7;#%",
        "eP?7[9k,",
        "E/}>2]kS",
        "A@y/2Tbq",
        "Gj8t3[5-",
        "f<K]7bEm",
        "LcX8v)>x",
        "f=B@Lx5Y",
        "KRhb5=%Z",
        "L3-Vxn_N",
        "Z8wKX{_J",
        "M49/WSv[",
        "Vjq.~E3%",
        "E-g9dWG_",
        "q:Ze^9Jp",
        "K2~PMrdD",
        "W6zr)5jX",
        "kLT$4MAq",
        "A&?Efy5)",
        "Lf`Y#z4^",
        "W8Sx3/u@",
        "ZJ\"h4Gr,"
    ]
    
    strengths = [
        # Very weak (0)
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        # Weak (1) 
        1, 1, 1, 1, 1, 1, 1, 1,
        # Moderate (2)
        2, 2, 2, 2, 2, 2, 2, 2,
        # Strong (3)
        3, 3, 3, 3, 3, 3, 3, 3,
        # Very strong (4) - original 6 + 42 new high-entropy passwords
        4, 4, 4, 4, 4, 4,  # Original 6
        4, 4, 4, 4, 4, 4, 4, 4, 4, 4,  # First 10 new passwords
        4, 4, 4, 4, 4, 4, 4, 4, 4, 4,  # Second 10 new passwords  
        4, 4, 4, 4, 4, 4, 4, 4, 4, 4,  # Third 10 new passwords
        4, 4, 4, 4, 4, 4, 4, 4, 4, 4,  # Fourth 10 new passwords
        4, 4  # Last 2 new passwords
    ]

    model = PasswordStrengthModel()
    model.train(passwords, strengths)
    return model


# Store the model globally
password_model = None


def load_password_model():
    """Load or initialize the password strength prediction model"""
    global password_model

    model_path = os.path.join(os.path.dirname(__file__),
                              '../password_model.pkl')

    password_model = PasswordStrengthModel()

    # Try to load an existing model
    if os.path.exists(model_path):
        try:
            success = password_model.load_model(model_path)
            if success:
                logging.info("Loaded existing password strength model")
                return
        except Exception as e:
            logging.error(f"Error loading password model: {str(e)}")

    # If no model exists or loading failed, initialize a default model
    logging.info("Initializing default password strength model")
    password_model = initialize_default_model()

    # Save the model for future use
    try:
        password_model.save_model(model_path)
    except Exception as e:
        logging.error(f"Error saving password model: {str(e)}")


def analyze_password(password):
    """
    Analyze password strength and provide feedback
    
    Args:
        password (str): The password to analyze
        
    Returns:
        dict: Analysis results including strength score, rating, and feedback
    """
    global password_model

    if not password_model:
        load_password_model()

    # Use ML model to predict strength category (0-4)
    strength_score = password_model.predict(password)

    # Convert NumPy types to Python native types for JSON serialization
    strength_score = int(strength_score)

    # Calculate common password metrics
    length = len(password)
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    # Generate feedback
    feedback = []
    if length < 8:
        feedback.append(
            "Password is too short (minimum 8 characters recommended)")
    if not has_lowercase:
        feedback.append("Add lowercase letters")
    if not has_uppercase:
        feedback.append("Add uppercase letters")
    if not has_digit:
        feedback.append("Add numbers")
    if not has_special:
        feedback.append("Add special characters")

    # If no specific issues found but strength is still low
    if not feedback and strength_score < 3:
        feedback.append("Avoid common patterns and dictionary words")

    # If password seems strong
    if length >= 12 and has_lowercase and has_uppercase and has_digit and has_special:
        feedback.append("Good password complexity")

    # Calculate entropy (rough estimate)
    charset_size = 0
    if has_lowercase: charset_size += 26
    if has_uppercase: charset_size += 26
    if has_digit: charset_size += 10
    if has_special: charset_size += 30  # Approximate special character count

    entropy = 0
    if charset_size > 0:
        entropy = float(length * (np.log2(charset_size)))

    # Map strength score to descriptive rating
    strength_ratings = [
        "Very Weak", "Weak", "Moderate", "Strong", "Very Strong"
    ]
    rating = strength_ratings[min(strength_score, 4)]

    return {
        'strength': strength_score,
        'rating': rating,
        'entropy': round(float(entropy), 1),
        'length': length,
        'has_lowercase': has_lowercase,
        'has_uppercase': has_uppercase,
        'has_digit': has_digit,
        'has_special': has_special,
        'feedback': feedback
    }
