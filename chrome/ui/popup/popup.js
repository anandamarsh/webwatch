// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded");
  
  // Get references to buttons
  const settingsButton = document.getElementById('settings-button');
  const toggleButton = document.getElementById('toggle-button');
  const statusElement = document.getElementById('status');
  const activityContainer = document.getElementById('activity-container');
  
  // Log which elements were found and which weren't
  console.log("Settings button found:", !!settingsButton);
  console.log("Toggle button found:", !!toggleButton);
  console.log("Status element found:", !!statusElement);
  console.log("Activity container found:", !!activityContainer);
  
  // Check current monitoring status
  chrome.storage.local.get(['monitoringPaused'], (result) => {
    const isPaused = result.monitoringPaused || false;
    // Define updateUI function
    function updateUI(isPaused) {
      if (toggleButton && statusElement) {
        updateToggleUI(isPaused, toggleButton, statusElement);
      }
    }
    updateUI(isPaused);
  });

  if (settingsButton) {
    settingsButton.addEventListener('click', openSettings);
  } else {
    console.error('Settings button not found in the DOM');
  }
  
  // Only try to add toggle functionality if the element exists
  if (toggleButton && statusElement) {
    // Check current monitoring state
    chrome.storage.sync.get(['monitoringEnabled'], function(result) {
      const isEnabled = result.monitoringEnabled !== false; // Default to true
      updateToggleUI(isEnabled, toggleButton, statusElement);
      
      // Add toggle event listener
      toggleButton.addEventListener('click', () => {
        const newState = !isEnabled;
        chrome.storage.sync.set({ monitoringEnabled: newState }, function() {
          updateToggleUI(newState, toggleButton, statusElement);
        });
      });
    });
  } else {
    console.error("Toggle button or status element not found");
  }
  
});

// Update the toggle UI based on state
function updateToggleUI(isEnabled, toggleButton, statusElement) {
  if (!toggleButton || !statusElement) {
    console.error("Toggle button or status element not found");
    return;
  }
  
  if (isEnabled) {
    toggleButton.textContent = 'Pause';
    toggleButton.classList.remove('button-secondary');
    toggleButton.classList.add('button-warning');
    statusElement.textContent = 'Monitoring is active';
    statusElement.className = 'status-active';
  } else {
    toggleButton.textContent = 'Resume';
    toggleButton.classList.remove('button-warning');
    toggleButton.classList.add('button-secondary');
    statusElement.textContent = 'Monitoring is paused';
    statusElement.className = 'status-paused';
  }
}


// Open settings
function openSettings() {
  chrome.tabs.create({ url: '../../ui/options/options.html' });
} 