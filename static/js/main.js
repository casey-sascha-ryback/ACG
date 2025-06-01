/**
 * Main JavaScript file for Cybersecurity Toolkit
 * Contains shared functionality across tools
 */

// Initialize tooltips and popovers when document is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize Bootstrap popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function(popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl, {
      html: true,
      sanitize: false
    });
  });
});

/**
 * Displays an alert message
 * 
 * @param {string} message - The message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {string} containerId - ID of the container element
 * @param {boolean} autoDismiss - Whether to automatically dismiss the alert
 */
function showAlert(message, type = 'info', containerId = 'alertContainer', autoDismiss = true) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Create alert element
  const alertEl = document.createElement('div');
  alertEl.className = `alert alert-${type} alert-dismissible fade show`;
  alertEl.role = 'alert';
  
  // Add message
  alertEl.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // Add to container
  container.appendChild(alertEl);
  
  // Auto dismiss after 5 seconds if requested
  if (autoDismiss) {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alertEl);
      bsAlert.close();
    }, 5000);
  }
}

/**
 * Creates and returns a card with educational information
 * 
 * @param {string} title - Card title
 * @param {string} content - Card content (can include HTML)
 * @param {string} type - Card type/color (primary, secondary, info, etc.)
 * @returns {HTMLElement} - The created card element
 */
function createInfoCard(title, content, type = 'info') {
  // Create card container
  const card = document.createElement('div');
  card.className = `card border-${type} mb-3`;
  
  // Create card header
  const cardHeader = document.createElement('div');
  cardHeader.className = `card-header bg-${type} bg-opacity-25 text-${type === 'light' ? 'dark' : type}`;
  cardHeader.innerHTML = `<strong>${title}</strong>`;
  
  // Create card body
  const cardBody = document.createElement('div');
  cardBody.className = 'card-body';
  cardBody.innerHTML = content;
  
  // Assemble card
  card.appendChild(cardHeader);
  card.appendChild(cardBody);
  
  return card;
}

/**
 * Creates an animated progress bar
 * 
 * @param {number} value - The progress value (0-100)
 * @param {string} type - The progress bar type (success, info, warning, danger)
 * @returns {HTMLElement} - The progress bar element
 */
function createProgressBar(value, type = 'primary') {
  // Container
  const container = document.createElement('div');
  container.className = 'progress';
  container.style.height = '25px';
  
  // Progress bar
  const progressBar = document.createElement('div');
  progressBar.className = `progress-bar progress-bar-striped progress-bar-animated bg-${type}`;
  progressBar.style.width = `${value}%`;
  progressBar.setAttribute('role', 'progressbar');
  progressBar.setAttribute('aria-valuenow', value);
  progressBar.setAttribute('aria-valuemin', '0');
  progressBar.setAttribute('aria-valuemax', '100');
  progressBar.textContent = `${value}%`;
  
  // Assemble
  container.appendChild(progressBar);
  
  return container;
}

/**
 * Copies text to clipboard
 * 
 * @param {string} text - Text to copy
 * @param {function} callback - Optional callback after copy
 */
function copyToClipboard(text, callback) {
  navigator.clipboard.writeText(text)
    .then(() => {
      if (callback && typeof callback === 'function') {
        callback(true);
      }
    })
    .catch(err => {
      console.error('Could not copy text: ', err);
      if (callback && typeof callback === 'function') {
        callback(false, err);
      }
    });
}

// Add copy button functionality to any pre element with code
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('pre.code-block').forEach(block => {
    // Create copy button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'btn btn-sm btn-outline-secondary copy-btn';
    copyBtn.innerHTML = '<i class="bi bi-clipboard"></i>';
    copyBtn.setAttribute('data-bs-toggle', 'tooltip');
    copyBtn.setAttribute('title', 'Copy to clipboard');
    
    // Add copy functionality
    copyBtn.addEventListener('click', function() {
      const code = block.querySelector('code')?.textContent || block.textContent;
      copyToClipboard(code, (success) => {
        if (success) {
          copyBtn.innerHTML = '<i class="bi bi-check"></i>';
          setTimeout(() => {
            copyBtn.innerHTML = '<i class="bi bi-clipboard"></i>';
          }, 2000);
        }
      });
    });
    
    // Add button to block
    block.style.position = 'relative';
    block.appendChild(copyBtn);
  });
});
