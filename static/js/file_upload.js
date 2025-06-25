/**
 * File Upload and Integrity Checking JavaScript
 * Handles file selection, checksum calculation, and verification
 */

document.addEventListener('DOMContentLoaded', function() {
  // File input elements
  const fileInput = document.getElementById('fileInput');
  const fileInputVerify = document.getElementById('fileInputVerify');
  const algorithmSelect = document.getElementById('algorithmSelect');
  const algorithmSelectVerify = document.getElementById('algorithmSelectVerify');
  const checksumInput = document.getElementById('checksumInput');
  
  // Button elements
  const calculateBtn = document.getElementById('calculateChecksumBtn');
  const verifyBtn = document.getElementById('verifyChecksumBtn');
  
  // Result containers
  const checksumResult = document.getElementById('checksumResult');
  const verifyResult = document.getElementById('verifyResult');
  
  // Set up file input change listeners to show selected file name
  if (fileInput) {
    fileInput.addEventListener('change', updateFileName);
  }
  
  if (fileInputVerify) {
    fileInputVerify.addEventListener('change', updateFileName);
  }
  
  // Calculate checksum button
  if (calculateBtn) {
    calculateBtn.addEventListener('click', function(e) {
      e.preventDefault();
      calculateChecksum();
    });
  }
  
  // Verify checksum button
  if (verifyBtn) {
    verifyBtn.addEventListener('click', function(e) {
      e.preventDefault();
      verifyChecksum();
    });
  }
  
  /**
   * Update file name display when a file is selected
   */
  function updateFileName(e) {
    const fileInput = e.target;
    const fileLabel = document.querySelector(`label[for="${fileInput.id}"]`);
    
    if (fileLabel) {
      const fileName = fileInput.files.length > 0 ? 
        fileInput.files[0].name : 
        'Choose file';
      
      // Update the label text
      if (fileLabel.querySelector('.custom-file-label')) {
        fileLabel.querySelector('.custom-file-label').textContent = fileName;
      } else {
        fileLabel.innerHTML = `${fileName} <i class="bi bi-paperclip"></i>`;
      }
    }
  }
  
  /**
   * Calculate file checksum
   */
  function calculateChecksum() {
    if (!fileInput || !algorithmSelect || !checksumResult) return;
    
    const file = fileInput.files[0];
    const algorithm = algorithmSelect.value;
    
    if (!file) {
      showAlert('Please select a file', 'warning', 'fileAlertContainer');
      return;
    }
    
    // Show loading indicator
    checksumResult.innerHTML = `
      <div class="text-center py-3">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Calculating checksum...</p>
      </div>
    `;
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('algorithm', algorithm);
    
    // Call API to calculate checksum
    fetch('/api/calculate-checksum', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        showAlert(data.error, 'danger', 'fileAlertContainer');
        checksumResult.innerHTML = '';
        return;
      }
      
      // Display the checksum result
      checksumResult.innerHTML = `
        <div class="card mt-3">
          <div class="card-header bg-success bg-opacity-25 text-success">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Checksum Generated</h5>
              <button type="button" id="copyChecksumBtn" class="btn btn-sm btn-outline-success">
                <i class="bi bi-clipboard"></i> Copy
              </button>
            </div>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <h6>File</h6>
              <p class="text-muted">${data.filename}</p>
            </div>
            <div class="mb-3">
              <h6>Algorithm</h6>
              <p class="text-muted">${data.algorithm.toUpperCase()}</p>
            </div>
            <div>
              <h6>Checksum</h6>
              <pre class="bg-light p-2 rounded overflow-auto"><code style="color:black;">${data.checksum}</code></pre>
            </div>
          </div>
        </div>
        
        <div class="card mt-3">
          <div class="card-header bg-info bg-opacity-25 text-info">
            <h5 class="mb-0">What is a File Checksum?</h5>
          </div>
          <div class="card-body">
            <p>A checksum (or hash) is a string of characters derived from a file's contents. 
            Even a tiny change to the file will produce a completely different checksum. This makes 
            checksums ideal for:</p>
            
            <ul>
              <li><strong>Verifying file integrity</strong> - Confirm a file hasn't been corrupted during download</li>
              <li><strong>Detecting unauthorized changes</strong> - Identify if a file has been tampered with</li>
              <li><strong>Validating authenticity</strong> - Ensure a file matches the original source</li>
            </ul>
            
            <div class="alert alert-primary">
              <i class="bi bi-info-circle-fill me-2"></i>
              Share this checksum with anyone who receives your file so they can verify its integrity.
            </div>
          </div>
        </div>
      `;
      
      // Add copy functionality to button
      const copyBtn = document.getElementById('copyChecksumBtn');
      if (copyBtn) {
        copyBtn.addEventListener('click', function() {
          copyToClipboard(data.checksum, (success) => {
            if (success) {
              copyBtn.innerHTML = '<i class="bi bi-check"></i> Copied!';
              setTimeout(() => {
                copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
              }, 2000);
            }
          });
        });
      }
    })
    .catch(error => {
      console.error('Error calculating checksum:', error);
      showAlert('Error calculating checksum. Please try again.', 'danger', 'fileAlertContainer');
      checksumResult.innerHTML = '';
    });
  }
  
  /**
   * Verify file checksum
   */
  function verifyChecksum() {
    if (!fileInputVerify || !algorithmSelectVerify || !checksumInput || !verifyResult) return;
    
    const file = fileInputVerify.files[0];
    const algorithm = algorithmSelectVerify.value;
    const checksum = checksumInput.value.trim();
    
    if (!file) {
      showAlert('Please select a file', 'warning', 'fileVerifyAlertContainer');
      return;
    }
    
    if (!checksum) {
      showAlert('Please enter a checksum to verify against', 'warning', 'fileVerifyAlertContainer');
      return;
    }
    
    // Show loading indicator
    verifyResult.innerHTML = `
      <div class="text-center py-3">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Verifying checksum...</p>
      </div>
    `;
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('algorithm', algorithm);
    formData.append('checksum', checksum);
    
    // Call API to verify checksum
    fetch('/api/verify-checksum', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        showAlert(data.error, 'danger', 'fileVerifyAlertContainer');
        verifyResult.innerHTML = '';
        return;
      }
      
      // Display the verification result
      const isValid = data.is_valid;
      const statusClass = isValid ? 'success' : 'danger';
      const statusIcon = isValid ? 'check-circle-fill' : 'x-circle-fill';
      const statusText = isValid ? 'Verification Successful' : 'Verification Failed';
      
      verifyResult.innerHTML = `
        <div class="card mt-3">
          <div class="card-header bg-${statusClass} bg-opacity-25 text-${statusClass}">
            <h5 class="mb-0">
              <i class="bi bi-${statusIcon} me-2"></i>
              ${statusText}
            </h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <h6>File</h6>
              <p class="text-muted">${data.filename}</p>
            </div>
            <div class="mb-3">
              <h6>Expected Checksum</h6>
              <pre class="bg-light p-2 rounded overflow-auto"><code>${data.provided_checksum}</code></pre>
            </div>
            <div class="mb-3">
              <h6>Calculated Checksum</h6>
              <pre class="bg-light p-2 rounded overflow-auto"><code>${data.calculated_checksum}</code></pre>
            </div>
            <div class="alert alert-${statusClass}">
              ${isValid ? 
                '<strong>File integrity verified!</strong> The file has not been modified.' : 
                '<strong>Integrity check failed!</strong> The file may be corrupted or tampered with.'}
            </div>
          </div>
        </div>
        
        ${!isValid ? `
        <div class="card mt-3">
          <div class="card-header bg-warning bg-opacity-25 text-warning">
            <h5 class="mb-0">Why Did Verification Fail?</h5>
          </div>
          <div class="card-body">
            <p>There are several reasons why the checksum verification might have failed:</p>
            
            <ul>
              <li><strong>Download corruption</strong> - The file may have been corrupted during download</li>
              <li><strong>File modification</strong> - The file may have been modified since the original checksum was created</li>
              <li><strong>Incorrect checksum provided</strong> - The expected checksum may have been entered incorrectly</li>
              <li><strong>Wrong algorithm selected</strong> - Make sure you're using the same algorithm that was used to generate the original checksum</li>
            </ul>
            
            <div class="alert alert-info">
              <i class="bi bi-info-circle-fill me-2"></i>
              Try downloading the file again or verifying the expected checksum value.
            </div>
          </div>
        </div>
        ` : ''}
      `;
    })
    .catch(error => {
      console.error('Error verifying checksum:', error);
      showAlert('Error verifying checksum. Please try again.', 'danger', 'fileVerifyAlertContainer');
      verifyResult.innerHTML = '';
    });
  }
});
