from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os
import numpy as np

class PasswordStrengthModel:
    """
    A model for predicting password strength using scikit-learn.
    This model uses character n-grams and length features to predict password strength.
    """
    def __init__(self):
        self.vectorizer = CountVectorizer(analyzer='char', ngram_range=(1, 3))
        self.model = LogisticRegression(max_iter=1000)
        self.is_trained = False
    
    def train(self, passwords, strengths):
        """
        Train the model with example passwords and their strength ratings.
        
        Args:
            passwords (list): List of password strings
            strengths (list): List of strength ratings (0-4, where 0 is very weak, 4 is very strong)
        """
        X_char = self.vectorizer.fit_transform(passwords)
        
        # Add length as a feature
        lengths = np.array([[len(pwd)] for pwd in passwords])
        X = np.hstack((X_char.toarray(), lengths))
        
        self.model.fit(X, strengths)
        self.is_trained = True
    
    def predict(self, password):
        """
        Predict the strength of a password.
        
        Args:
            password (str): The password to evaluate
            
        Returns:
            int: Predicted strength (0-4)
        """
        if not self.is_trained:
            return 2  # Default medium strength if model not trained
        
        # Transform the password
        X_char = self.vectorizer.transform([password])
        
        # Add length as a feature
        length = np.array([[len(password)]])
        X = np.hstack((X_char.toarray(), length))
        
        # Predict strength
        return self.model.predict(X)[0]
    
    def save_model(self, filepath):
        """Save the trained model to a file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'model': self.model,
                'is_trained': self.is_trained
            }, f)
    
    def load_model(self, filepath):
        """Load a trained model from a file"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.vectorizer = data['vectorizer']
                self.model = data['model']
                self.is_trained = data['is_trained']
            return True
        return False

# Initialize a default model with common password patterns
def initialize_default_model():
    model = PasswordStrengthModel()
    
    # Example training data (would be much larger in a real implementation)
    passwords = [
        "password", "123456", "qwerty", "admin", "welcome",  # Very weak (0)
        "password123", "admin123", "welcome1",               # Weak (1)
        "P@ssword", "Secur1ty", "Welc0me",                   # Medium (2)
        "P@ssw0rd123", "S3cur1ty!", "W3lc0me@Home",          # Strong (3)
        "P@$$w0rd123!", "S3cur1ty@2023!", "W3lc0me@H0me2023" # Very strong (4)
    ]
    
    strengths = [
        0, 0, 0, 0, 0,  # Very weak
        1, 1, 1,        # Weak
        2, 2, 2,        # Medium
        3, 3, 3,        # Strong
        4, 4, 4         # Very strong
    ]
    
    model.train(passwords, strengths)
    return model
