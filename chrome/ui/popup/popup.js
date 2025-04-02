// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded");
  
  // Get references to buttons
  const dashboardButton = document.getElementById('dashboard-button');
  const settingsButton = document.getElementById('settings-button');
  const toggleButton = document.getElementById('toggle-button');
  const statusElement = document.getElementById('status');
  const activityContainer = document.getElementById('activity-container');
  
  // Log which elements were found and which weren't
  console.log("Dashboard button found:", !!dashboardButton);
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
  
  // Add event listeners if elements exist
  if (dashboardButton) {
    dashboardButton.addEventListener('click', openDashboard);
  } else {
    console.error('Dashboard button not found in the DOM');
  }
  
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
  
  // Load stats and recent activity
  loadStats();
  loadRecentActivity();
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

// Load statistics
function loadStats() {
  const todayCountElement = document.getElementById('today-count');
  const weekCountElement = document.getElementById('week-count');
  const totalCountElement = document.getElementById('total-count');
  
  if (!todayCountElement || !weekCountElement || !totalCountElement) {
    console.error("One or more stat elements not found");
    return;
  }
  
  fetch('http://localhost:1978/stats')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Calculate today's count
      const todayCount = data.daily_visits && data.daily_visits.length > 0 ? 
        data.daily_visits[data.daily_visits.length - 1].count : 0;
      
      // Calculate week count (sum of last 7 days)
      const weekCount = data.daily_visits ?
        data.daily_visits
          .slice(-7)
          .reduce((sum, day) => sum + day.count, 0) : 0;
      
      // Update the UI
      todayCountElement.textContent = todayCount;
      weekCountElement.textContent = weekCount;
      totalCountElement.textContent = data.total_visits || 0;
    })
    .catch(error => {
      console.error('Error fetching stats:', error);
      todayCountElement.textContent = '-';
      weekCountElement.textContent = '-';
      totalCountElement.textContent = '-';
    });
}

// Load recent activity
function loadRecentActivity() {
  const activityContainer = document.getElementById('activity-container');
  
  if (!activityContainer) {
    console.error("Activity container not found");
    return;
  }
  
  fetch('http://localhost:1978/report?days=1&limit=5')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      if (data.visits && data.visits.length > 0) {
        const activityList = document.createElement('div');
        activityList.className = 'activity-list';
        
        data.visits.forEach(visit => {
          const activityItem = document.createElement('div');
          activityItem.className = 'activity-item';
          
          // Format the timestamp
          const visitTime = new Date(visit.timestamp);
          const timeString = visitTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          
          activityItem.innerHTML = `
            <div class="activity-title">${visit.title || 'Untitled'}</div>
            <div class="activity-url">${visit.url}</div>
            <div class="activity-time">${timeString}</div>
          `;
          
          // Add click event to open the URL
          activityItem.addEventListener('click', () => {
            chrome.tabs.create({ url: visit.url });
          });
          
          activityList.appendChild(activityItem);
        });
        
        activityContainer.innerHTML = '';
        activityContainer.appendChild(activityList);
      } else {
        activityContainer.innerHTML = '<div class="loading">No recent activity</div>';
      }
    })
    .catch(error => {
      console.error('Error fetching recent activity:', error);
      activityContainer.innerHTML = `
        <div class="error">
          Could not load recent activity.<br>
          Make sure the WebWatch server is running.
        </div>
      `;
    });
}

// Open the dashboard
function openDashboard() {
  chrome.tabs.create({ url: 'http://localhost:1978/dashboard' });
}

// Open settings
function openSettings() {
  chrome.tabs.create({ url: '../../ui/options/options.html' });
} 