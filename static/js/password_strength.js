/**
 * Password Strength Analysis Visualization
 * Provides interactive visualization of password strength
 */

document.addEventListener('DOMContentLoaded', function() {
  const passwordInput = document.getElementById('passwordInput');
  const submitButton = document.getElementById('analyzePasswordBtn');
  const clearButton = document.getElementById('clearPasswordBtn');
  const resultContainer = document.getElementById('passwordAnalysisResult');
  const strengthMeter = document.getElementById('strengthMeter');
  const strengthLabel = document.getElementById('strengthLabel');
  const feedbackList = document.getElementById('feedbackList');
  const showPasswordToggle = document.getElementById('showPasswordToggle');
  
  // Initialize password visibility toggle
  if (showPasswordToggle && passwordInput) {
    showPasswordToggle.addEventListener('click', function() {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      showPasswordToggle.innerHTML = type === 'password' ? 
        '<i class="bi bi-eye"></i>' : 
        '<i class="bi bi-eye-slash"></i>';
    });
  }
  
  // Clear button functionality
  if (clearButton) {
    clearButton.addEventListener('click', function() {
      // Clear password input
      if (passwordInput) {
        passwordInput.value = '';
      }
      
      // Reset strength meter
      if (strengthMeter && strengthLabel) {
        strengthMeter.style.width = '0%';
        strengthMeter.className = 'progress-bar';
        strengthMeter.setAttribute('aria-valuenow', 0);
        strengthLabel.textContent = 'Not Analyzed';
        strengthLabel.className = 'badge bg-secondary';
      }
      
      // Reset feedback list
      if (feedbackList) {
        feedbackList.innerHTML = `
          <li class="list-group-item text-center py-3">
            <i class="bi bi-arrow-up-circle me-2"></i>
            Enter a password above to receive analysis and recommendations.
          </li>
        `;
      }
      
      // Clear results
      if (resultContainer) {
        resultContainer.innerHTML = '';
      }
      
      // Clear any alerts
      const alertContainer = document.getElementById('passwordAlertContainer');
      if (alertContainer) {
        alertContainer.innerHTML = '';
      }
    });
  }
  
  // Handle password analysis
  if (passwordInput) {
    // Trigger analysis on password input (with debounce)
    let debounceTimer;
    passwordInput.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      
      // Only analyze if sufficiently complex to avoid too many requests
      if (passwordInput.value.length > 3) {
        debounceTimer = setTimeout(analyzePassword, 500);
      } else if (strengthMeter) {
        // Reset meter for very short passwords
        updateStrengthMeter(0);
      }
    });
    
    // Keep the click handler for the submit button if it exists (for compatibility)
    if (submitButton) {
      submitButton.addEventListener('click', function(e) {
        e.preventDefault();
        analyzePassword();
      });
    }
  }
  
  /**
   * Analyze password strength via API
   */
  function analyzePassword() {
    const password = passwordInput.value;
    if (!password) {
      showAlert('Please enter a password to analyze', 'warning', 'passwordAlertContainer');
      return;
    }
    
    // Show loading spinner
    resultContainer.innerHTML = `
      <div class="text-center my-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Analyzing password strength...</p>
      </div>
    `;
    
    // Prepare form data
    const formData = new FormData();
    formData.append('password', password);
    
    // Send request to server
    fetch('/api/analyze-password', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      displayPasswordAnalysis(data);
    })
    .catch(error => {
      console.error('Error analyzing password:', error);
      showAlert('Error analyzing password. Please try again.', 'danger', 'passwordAlertContainer');
    });
  }
  
  /**
   * Display password analysis results
   * 
   * @param {Object} data - Password analysis data from API
   */
  function displayPasswordAnalysis(data) {
    if (data.error) {
      showAlert(data.error, 'danger', 'passwordAlertContainer');
      return;
    }
    
    // Update strength meter
    updateStrengthMeter(data.strength);
    
    // Update feedback list
    if (feedbackList) {
      feedbackList.innerHTML = '';
      
      if (data.feedback && data.feedback.length > 0) {
        data.feedback.forEach(item => {
          const li = document.createElement('li');
          li.className = 'list-group-item';
          li.innerHTML = item;
          feedbackList.appendChild(li);
        });
      } else {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerHTML = 'Password meets security criteria!';
        feedbackList.appendChild(li);
      }
    }
    
    // Create detailed report
    resultContainer.innerHTML = `
      <div class="card mb-4">
        <div class="card-header bg-primary bg-opacity-25 text-primary">
          <h5 class="mb-0">Password Analysis Report</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <h6>Strength Rating</h6>
              <p class="fs-4 fw-bold ${getStrengthTextClass(data.strength)}">${data.rating}</p>
              
              <h6>Password Properties</h6>
              <ul class="list-group list-group-flush mb-3">
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  Length
                  <span class="badge bg-secondary rounded-pill">${data.length} characters</span>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  Lowercase Letters
                  <span class="badge ${data.has_lowercase ? 'bg-success' : 'bg-danger'} rounded-pill">
                    ${data.has_lowercase ? 'Yes' : 'No'}
                  </span>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  Uppercase Letters
                  <span class="badge ${data.has_uppercase ? 'bg-success' : 'bg-danger'} rounded-pill">
                    ${data.has_uppercase ? 'Yes' : 'No'}
                  </span>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  Numbers
                  <span class="badge ${data.has_digit ? 'bg-success' : 'bg-danger'} rounded-pill">
                    ${data.has_digit ? 'Yes' : 'No'}
                  </span>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  Special Characters
                  <span class="badge ${data.has_special ? 'bg-success' : 'bg-danger'} rounded-pill">
                    ${data.has_special ? 'Yes' : 'No'}
                  </span>
                </li>
              </ul>
            </div>
            <div class="col-md-6">
              <h6>Entropy</h6>
              <p class="fs-5">${data.entropy} bits</p>
              <div class="progress mb-3" style="height: 20px;">
                <div class="progress-bar bg-info" role="progressbar" 
                    style="width: ${Math.min(100, data.entropy / 128 * 100)}%;" 
                    aria-valuenow="${data.entropy}" aria-valuemin="0" aria-valuemax="128">
                  ${data.entropy} bits
                </div>
              </div>
              <p class="small text-muted">Entropy measures the randomness and unpredictability of your password. 
              Higher values mean greater security. Values above 60 bits are good for general use, 
              while critical applications should exceed 80 bits.</p>
                            
              <h6>Time to Crack (Estimated)</h6>
              <p class="fs-5">${estimateCrackTime(data.entropy)}</p>
              <p class="small text-muted">Based on entropy and assuming a modern attacker with multiple GPUs 
              capable of billions of attempts per second.</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header bg-info bg-opacity-25 text-info">
          <h5 class="mb-0">Educational Insights</h5>
        </div>
        <div class="card-body">
          <h6>Why Password Strength Matters</h6>
          <p>Strong passwords are your first line of defense against unauthorized access. 
          Weak passwords can be cracked through various methods:</p>
          <ul>
            <li><strong>Dictionary Attacks</strong>: Trying common words and phrases</li>
            <li><strong>Brute Force</strong>: Systematically trying all possible combinations</li>
            <li><strong>Social Engineering</strong>: Using personal information to guess passwords</li>
          </ul>
          
          <h6>Password Best Practices</h6>
          <ul>
            <li>Use a <strong>unique password</strong> for each account</li>
            <li>Aim for <strong>at least 12 characters</strong></li>
            <li>Include a <strong>mix of character types</strong></li>
            <li>Consider using a <strong>password manager</strong></li>
            <li>Enable <strong>multi-factor authentication</strong> where available</li>
          </ul>
          
          <h6>The Challenge of Human Memory</h6>
          <p>Humans struggle to remember complex random strings, which leads to insecure practices like reusing 
          passwords or using simple variations. Password managers solve this problem by generating and storing 
          strong unique passwords for each service.</p>
        </div>
      </div>
    `;
  }
  
  /**
   * Update the strength meter visualization
   * 
   * @param {number} strength - Strength score (0-4)
   */
  function updateStrengthMeter(strength) {
    if (!strengthMeter || !strengthLabel) return;
    
    // Map strength to percentage and color
    const percentage = (strength / 4) * 100;
    const color = getStrengthColor(strength);
    const label = getStrengthLabel(strength);
    
    // Update progress bar
    strengthMeter.style.width = `${percentage}%`;
    strengthMeter.className = `progress-bar progress-bar-striped bg-${color}`;
    strengthMeter.setAttribute('aria-valuenow', percentage);
    
    // Update label
    strengthLabel.textContent = label;
    strengthLabel.className = `text-${color}`;
  }
  
  /**
   * Get color class based on strength score
   * 
   * @param {number} strength - Strength score (0-4)
   * @returns {string} - Bootstrap color class
   */
  function getStrengthColor(strength) {
    switch (strength) {
      case 0: return 'danger';
      case 1: return 'warning';
      case 2: return 'info';
      case 3: return 'primary';
      case 4: return 'success';
      default: return 'secondary';
    }
  }
  
  /**
   * Get text class for strength label
   * 
   * @param {number} strength - Strength score (0-4)
   * @returns {string} - Bootstrap text color class
   */
  function getStrengthTextClass(strength) {
    switch (strength) {
      case 0: return 'text-danger';
      case 1: return 'text-warning';
      case 2: return 'text-info';
      case 3: return 'text-primary';
      case 4: return 'text-success';
      default: return 'text-secondary';
    }
  }
  
  /**
   * Get strength label based on score
   * 
   * @param {number} strength - Strength score (0-4)
   * @returns {string} - Label text
   */
  function getStrengthLabel(strength) {
    switch (strength) {
      case 0: return 'Very Weak';
      case 1: return 'Weak';
      case 2: return 'Moderate';
      case 3: return 'Strong';
      case 4: return 'Very Strong';
      default: return 'Unknown';
    }
  }
  
  /**
   * Estimate password crack time based on entropy
   * 
   * @param {number} entropy - Password entropy in bits
   * @returns {string} - Human-readable estimate
   */
  function estimateCrackTime(entropy) {
    // Assume a billion guesses per second (modern attacker with GPUs)
    const guessesPerSecond = 1000000000;
    const possibleCombinations = Math.pow(2, entropy);
    const secondsToBreak = possibleCombinations / guessesPerSecond / 2; // Average case is half the total
    
    // Convert to human-readable time
    if (secondsToBreak < 1) {
      return 'Instantly';
    } else if (secondsToBreak < 60) {
      return `${secondsToBreak.toFixed(2)} seconds`;
    } else if (secondsToBreak < 3600) {
      return `${(secondsToBreak / 60).toFixed(2)} minutes`;
    } else if (secondsToBreak < 86400) {
      return `${(secondsToBreak / 3600).toFixed(2)} hours`;
    } else if (secondsToBreak < 31536000) {
      return `${(secondsToBreak / 86400).toFixed(2)} days`;
    } else if (secondsToBreak < 3153600000) {
      return `${(secondsToBreak / 31536000).toFixed(2)} years`;
    } else if (secondsToBreak < 3153600000 * 1000) {
      return `${(secondsToBreak / 31536000).toFixed(0)} years`;
    } else {
      return 'Millions of years+';
    }
  }
});
