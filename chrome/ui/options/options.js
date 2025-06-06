document.addEventListener('DOMContentLoaded', function() {
  const tabs = document.querySelectorAll('.tab');
  const tabContents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      tabs.forEach(t => t.classList.remove('active'));
      tabContents.forEach(tc => tc.classList.remove('active'));

      this.classList.add('active');
      document.getElementById(this.dataset.tab).classList.add('active');

      // Trigger fresh load from server when switching tabs
      if (this.dataset.tab === 'history') {
        loadHistory();
      } else if (this.dataset.tab === 'blocklist') {
        loadBlocklist();
      }
    });
  });

  // Load initial data
  loadHistory();
  loadBlocklist();
});

// Set up event listeners

document.getElementById('add-block-button').addEventListener('click', addBlockedUrl);



// Set up history search

// Get the server URL from settings
function getServerUrl() {
  return new Promise((resolve) => {
    chrome.storage.sync.get({
      serverUrl: 'http://localhost:1978'
    }, function(items) {
      resolve(items.serverUrl);
    });
  });
}

// Load settings from storage
function loadSettings() {
  chrome.storage.sync.get({
    serverUrl: 'http://localhost:1978',
    trackIncognito: false,
    trackLocal: true
  }, function(items) {
    document.getElementById('server-url').value = items.serverUrl;
    document.getElementById('track-incognito').checked = items.trackIncognito;
    document.getElementById('track-local').checked = items.trackLocal;
  });
}

// Save settings to storage
function saveSettings() {
  const serverUrl = document.getElementById('server-url').value;
  const trackIncognito = document.getElementById('track-incognito').checked;
  const trackLocal = document.getElementById('track-local').checked;
  
  chrome.storage.sync.set({
    serverUrl: serverUrl,
    trackIncognito: trackIncognito,
    trackLocal: trackLocal
  }, function() {
    showStatus('Settings saved successfully!', 'success');
    
    // Reload blocklist with new server URL
    loadBlocklist();
  });
}

// Reset settings to defaults
function resetSettings() {
  document.getElementById('server-url').value = 'http://localhost:1978';
  document.getElementById('track-incognito').checked = false;
  document.getElementById('track-local').checked = true;
  
  chrome.storage.sync.set({
    serverUrl: 'http://localhost:1978',
    trackIncognito: false,
    trackLocal: true
  }, function() {
    showStatus('Settings reset to defaults!', 'success');
    
    // Reload blocklist with default server URL
    loadBlocklist();
  });
}

// Load blocklist from API
async function loadBlocklist() {
  const blocklistContainer = document.getElementById('blocklist-container');
  blocklistContainer.innerHTML = '<div class="loading">Loading blocklist...</div>';
  
  try {
    const serverUrl = localStorage.getItem('serverUrl') || 'http://localhost:1978';
    const response = await fetch(`${serverUrl}/api/blocklist`);
    
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }
    
    let blocklist = await response.json();
    
    // Sort blocklist by timestamp or reverse the order to show latest on top
    blocklist = blocklist.reverse(); // Assuming entries are added sequentially
    
    if (!blocklist || blocklist.length === 0) {
      blocklistContainer.innerHTML = '<div class="empty-message">No blocked URLs found.</div>';
      return;
    }
    
    const blocklistHTML = blocklist.map((entry, index) => `
      <div class="blocklist-item">
        <div class="blocklist-url">${entry.url}</div>
        <div class="blocklist-reason">${entry.reason || 'No reason provided'}</div>
        <button class="delete-icon" title="Delete" data-index="${index}">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/>
        </svg>
    </button>
      </div>
    `).join('');
    
    blocklistContainer.innerHTML = blocklistHTML;
    
    // Add event listeners for delete buttons
    document.querySelectorAll('.delete-icon').forEach(button => {
      button.addEventListener('click', async (e) => {
        const index = button.dataset.index;
        try {
          const deleteResponse = await fetch(`${serverUrl}/api/blocklist/${index}`, {
            method: 'DELETE'
          });
          if (!deleteResponse.ok) {
            throw new Error(`Failed to delete entry: ${deleteResponse.status}`);
          }
          loadBlocklist(); // Refresh the blocklist after deletion
        } catch (error) {
          console.error('Error deleting blocklist entry:', error);
        }
      });
    });
  } catch (error) {
    console.error('Error loading blocklist:', error);
    blocklistContainer.innerHTML = `<div class="empty-message">Error loading blocklist: ${error.message}</div>`;
  }
}

// Add a URL to the blocklist
async function addBlockedUrl() {
  const urlInput = document.getElementById('block-url');
  const reasonInput = document.getElementById('block-reason');
  
  const url = urlInput.value.trim();
  const reason = reasonInput.value.trim();
  
  if (!url) {
    showStatus('Please enter a URL to block', 'error');
    return;
  }
  
  try {
    const serverUrl = await getServerUrl();
    
    const response = await fetch(`${serverUrl}/api/blocklist`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: url,
        reason: reason || 'Manually blocked'
      })
    });
    
    const result = await response.json();
    
    if (!response.ok || result.error) {
      throw new Error(result.error || `Server returned ${response.status}`);
    }
    
    // Clear inputs
    urlInput.value = '';
    reasonInput.value = '';
    
    showStatus(`URL "${url}" added to blocklist!`, 'success');
    
    // Reload the blocklist
    loadBlocklist();
    
    // If history tab is active, reload history to update block status icons
    if (document.getElementById('history').classList.contains('active')) {
      loadHistory();
    }
    
  } catch (error) {
    console.error('Error adding blocked URL:', error);
    showStatus(`Error: ${error.message}`, 'error');
  }
}

// Remove a URL from the blocklist
async function removeBlockedUrl(url, itemElement) {
  // First, add a visual indication that the item is being removed
  if (itemElement) {
    itemElement.style.opacity = '0.5';
  }
  
  try {
    const serverUrl = await getServerUrl();
    
    const response = await fetch(`${serverUrl}/api/blocklist/${encodeURIComponent(url)}`, {
      method: 'DELETE'
    });
    
    const result = await response.json();
    
    if (!response.ok || result.error) {
      // If there was an error, restore the item
      if (itemElement) {
        itemElement.style.opacity = '1';
      }
      throw new Error(result.error || `Server returned ${response.status}`);
    }
    
    // Remove the item from the DOM if element was provided
    if (itemElement) {
      itemElement.remove();
      
      // If no items left, show empty message
      const blocklistContainer = document.getElementById('blocklist-container');
      if (blocklistContainer.querySelectorAll('.blocklist-item').length === 0) {
        blocklistContainer.innerHTML = '<div class="empty-message">No blocked URLs. Add one below.</div>';
      }
    }
    
    showStatus(`URL "${url}" removed from blocklist!`, 'success');
    
    // Reload the blocklist
    loadBlocklist();
    
    // If history tab is active, reload history to update block status icons
    if (document.getElementById('history').classList.contains('active')) {
      loadHistory();
    }
    
  } catch (error) {
    console.error('Error removing blocked URL:', error);
    showStatus(`Error: ${error.message}`, 'error');
  }
}

// Function to load and display history data
async function loadHistory() {
  const historyContainer = document.getElementById('history-container');
  historyContainer.innerHTML = '<div class="loading">Loading browsing history...</div>';
  
  try {
    const serverUrl = localStorage.getItem('serverUrl') || 'http://localhost:1978';
    
    // Fetch blocklist to determine blocked status
    const blocklistResponse = await fetch(`${serverUrl}/api/blocklist`);
    if (!blocklistResponse.ok) {
      throw new Error(`Server returned ${blocklistResponse.status}: ${blocklistResponse.statusText}`);
    }
    const blocklist = await blocklistResponse.json();
    const blockedUrls = new Set(blocklist.map(entry => entry.url));
    
    // Fetch history from API
    const response = await fetch(`${serverUrl}/api/visits?days=30&limit=1000`);
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }
    const apiVisits = await response.json();
    
    // Fetch history from Chrome
    const chromeVisits = await new Promise((resolve, reject) => {
      chrome.history.search({ text: '', maxResults: 1000, startTime: Date.now() - (30 * 24 * 60 * 60 * 1000) }, (historyItems) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(historyItems.map(item => ({
            url: item.url,
            title: item.title,
            timestamp: new Date(item.lastVisitTime).toISOString()
          })));
        }
      });
    });
    
    // Combine and deduplicate visits
    const allVisits = [...apiVisits, ...chromeVisits];
    const uniqueVisitsMap = new Map();
    
    allVisits.forEach(visit => {
      // Discard URLs starting with chrome-extension: and localhost:
      if (visit.url.startsWith('chrome-extension:') || visit.url.startsWith('http://localhost:') || visit.url.startsWith('https://localhost:')) {
        return;
      }
      
      if (!uniqueVisitsMap.has(visit.url) || new Date(visit.timestamp) > new Date(uniqueVisitsMap.get(visit.url).timestamp)) {
        uniqueVisitsMap.set(visit.url, visit);
      }
    });
    
    const uniqueVisits = Array.from(uniqueVisitsMap.values());
    
    // Sort visits by timestamp (newest first)
    uniqueVisits.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    if (uniqueVisits.length === 0) {
      historyContainer.innerHTML = '<div class="empty-message">No browsing history found.</div>';
      return;
    }
    
    // Group visits by domain
    const domainMap = {};
    
    uniqueVisits.forEach(visit => {
      try {
        const url = new URL(visit.url);
        const domain = url.hostname;
        
        if (!domainMap[domain]) {
          domainMap[domain] = {
            domain: domain,
            visits: [],
            count: 0
          };
        }
        
        domainMap[domain].visits.push(visit);
        domainMap[domain].count++;
      } catch (e) {
        console.error(`Invalid URL: ${visit.url}`, e);
      }
    });
    
    // Sort domains by visit count
    const sortedDomains = Object.values(domainMap).sort((a, b) => b.count - a.count);
    
    // Create HTML for each domain group
    const historyHTML = sortedDomains.map(domainGroup => {
      const { domain, visits, count } = domainGroup;
      
      // Create HTML for each visit
      const visitsHTML = visits.map(visit => {
        const date = new Date(visit.timestamp);
        const formattedDate = date.toLocaleString();
        const isBlocked = blockedUrls.has(visit.url);
        
        return `
          <div class="history-item" data-url="${visit.url}" data-blocked="${isBlocked}">
            <div class="history-details">
              <div class="history-title">${visit.title || 'Untitled'}</div>
              <div class="history-url">${visit.url}</div>
              <div class="history-time">${formattedDate}</div>
            </div>
            <button class="history-toggle ${isBlocked ? 'blocked' : 'allowed'}" title="${isBlocked ? 'Unblock this URL' : 'Block this URL'}">
              ${isBlocked ? `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8 0-1.85.63-3.55 1.69-4.9L16.9 18.31C15.55 19.37 13.85 20 12 20zm6.31-3.1L7.1 5.69C8.45 4.63 10.15 4 12 4c4.42 0 8 3.58 8 8 0 1.85-.63 3.55-1.69 4.9z"/>
                </svg>
              ` : `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              `}
            </button>
          </div>
        `;
      }).join('');
      
      return `
        <div class="history-domain">
          <div class="history-domain-header">
            <div class="expand-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18">
                <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6-6-6z"/>
              </svg>
            </div>
            <div class="history-domain-name">${domain}</div>
            <div class="history-domain-count">${count} visits</div>
          </div>
          <div class="history-domain-urls">
            ${visitsHTML}
          </div>
        </div>
      `;
    }).join('');
    
    historyContainer.innerHTML = historyHTML;
    
    // Add event listeners for domain expansion
    document.querySelectorAll('.history-domain-header').forEach(header => {
      header.addEventListener('click', () => {
        const domain = header.closest('.history-domain');
        domain.classList.toggle('expanded');
      });
    });

    // Add event listeners for toggle buttons
    document.querySelectorAll('.history-toggle').forEach(button => {
      button.addEventListener('click', (event) => {
        const itemElement = event.target.closest('.history-item');
        const url = itemElement.getAttribute('data-url');
        const currentlyBlocked = itemElement.getAttribute('data-blocked') === 'true';
        toggleBlockedStatus(url, currentlyBlocked, itemElement);
      });
    });
    
  } catch (error) {
    console.error('Error loading history:', error);
    historyContainer.innerHTML = `<div class="empty-message">Error loading history: ${error.message}</div>`;
  }
}

// Toggle a URL's blocked status
async function toggleBlockedStatus(url, currentlyBlocked, itemElement) {
  if (currentlyBlocked) {
    // If currently blocked, remove from blocklist
    await removeBlockedUrl(url);
  } else {
    // If not blocked, add to blocklist
    try {
      const serverUrl = await getServerUrl();
      
      const response = await fetch(`${serverUrl}/api/blocklist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: url,
          reason: 'Blocked from history'
        })
      });
      
      const result = await response.json();
      
      if (!response.ok || result.error) {
        throw new Error(result.error || `Server returned ${response.status}`);
      }
      
      showStatus(`URL "${url}" added to blocklist!`, 'success');
    } catch (error) {
      console.error('Error adding URL to blocklist:', error);
      showStatus(`Error: ${error.message}`, 'error');
      return;
    }
  }
  
  // Update the UI
  if (itemElement) {
    const newStatus = !currentlyBlocked;
    itemElement.setAttribute('data-blocked', newStatus ? 'true' : 'false');
    
    const toggleButton = itemElement.querySelector('.history-toggle');
    if (toggleButton) {
      toggleButton.className = `history-toggle ${newStatus ? 'blocked' : 'allowed'}`;
      toggleButton.title = newStatus ? 'Unblock this URL' : 'Block this URL';
    } else {
      console.error('Toggle button not found within itemElement:', itemElement);
    }
  }
  
  // Reload the blocklist
  loadBlocklist();
}

// Update the isUrlInBlocklist function to handle domain: prefix
function isUrlInBlocklist(url, blocklist) {
  // Handle domain: prefix explicitly
  if (url.startsWith('domain:')) {
    const domainToCheck = url.substring(7); // Remove 'domain:' prefix
    
    for (const item of blocklist) {
      // Check for exact domain block
      if (item.url === url) {
        return true;
      }
      
      // Check for domain block with different prefix
      if (item.url.startsWith('domain:') && 
          item.url.substring(7) === domainToCheck) {
        return true;
      }
    }
    return false;
  }
  
  // Create URL object for easier domain extraction
  let urlObj;
  try {
    urlObj = new URL(url);
  } catch (e) {
    console.error('Invalid URL:', url);
    return false;
  }
  
  // Extract the domain from the URL
  const domain = urlObj.hostname;
  
  for (const item of blocklist) {
    const blockedUrl = item.url;
    
    // Exact match
    if (url === blockedUrl) {
      return true;
    }
    
    // Domain match (if blocked URL starts with domain:)
    if (blockedUrl.startsWith('domain:')) {
      const blockedDomain = blockedUrl.substring(7); // Remove 'domain:' prefix
      if (domain === blockedDomain || domain.endsWith('.' + blockedDomain)) {
        return true;
      }
    }
    
    // Wildcard domain match (for *.example.com/* patterns)
    if (blockedUrl.startsWith('*.') && blockedUrl.includes('/*')) {
      const blockedDomain = blockedUrl.substring(2, blockedUrl.indexOf('/*'));
      if (domain === blockedDomain || domain.endsWith('.' + blockedDomain)) {
        return true;
      }
    }
    
    // Pattern match (if blocked URL contains *)
    if (blockedUrl.includes('*')) {
      // Convert wildcard pattern to regex
      const pattern = blockedUrl
        .replace(/\./g, '\\.')
        .replace(/\*/g, '.*');
      const regex = new RegExp(`^${pattern}$`);
      if (regex.test(url)) {
        return true;
      }
    }
  }
  
  return false;
}

// Filter history items
function filterHistory(filter) {
  // Update active button
  document.querySelectorAll('.filter-button').forEach(button => {
    button.classList.remove('active');
  });
  document.getElementById(`filter-${filter}`).classList.add('active');
  
  // Filter items
  const historyItems = document.querySelectorAll('.history-item');
  historyItems.forEach(item => {
    const isBlocked = item.getAttribute('data-blocked') === 'true';
    
    if (filter === 'all' || 
        (filter === 'blocked' && isBlocked) || 
        (filter === 'allowed' && !isBlocked)) {
      item.style.display = '';
    } else {
      item.style.display = 'none';
    }
  });
  
  // Check if any items are visible
  let visibleItems = 0;
  historyItems.forEach(item => {
    if (item.style.display !== 'none') {
      visibleItems++;
    }
  });
  
  // Show empty message if no items are visible
  const historyContainer = document.getElementById('history-container');
  const emptyMessage = historyContainer.querySelector('.empty-message');
  
  if (visibleItems === 0 && !emptyMessage) {
    const messageElement = document.createElement('div');
    messageElement.className = 'empty-message';
    messageElement.textContent = `No ${filter} URLs found.`;
    historyContainer.appendChild(messageElement);
  } else if (visibleItems > 0 && emptyMessage) {
    emptyMessage.remove();
  }
}

// Search history items
function searchHistory() {
  const searchTerm = document.getElementById('history-search').value.toLowerCase();
  const historyItems = document.querySelectorAll('.history-item');
  
  historyItems.forEach(item => {
    const title = item.querySelector('.history-title').textContent.toLowerCase();
    const url = item.querySelector('.history-url').textContent.toLowerCase();
    
    if (title.includes(searchTerm) || url.includes(searchTerm)) {
      // Only show if it also matches the current filter
      const currentFilter = document.querySelector('.filter-button.active').id.replace('filter-', '');
      const isBlocked = item.getAttribute('data-blocked') === 'true';
      
      if (currentFilter === 'all' || 
          (currentFilter === 'blocked' && isBlocked) || 
          (currentFilter === 'allowed' && !isBlocked)) {
        item.style.display = '';
      } else {
        item.style.display = 'none';
      }
    } else {
      item.style.display = 'none';
    }
  });
  
  // Check if any items are visible
  let visibleItems = 0;
  historyItems.forEach(item => {
    if (item.style.display !== 'none') {
      visibleItems++;
    }
  });
  
  // Show empty message if no items are visible
  const historyContainer = document.getElementById('history-container');
  let emptyMessage = historyContainer.querySelector('.empty-message');
  
  if (visibleItems === 0 && !emptyMessage) {
    emptyMessage = document.createElement('div');
    emptyMessage.className = 'empty-message';
    emptyMessage.textContent = searchTerm ? `No results found for "${searchTerm}".` : 'No matching URLs found.';
    historyContainer.appendChild(emptyMessage);
  } else if (visibleItems > 0 && emptyMessage) {
    emptyMessage.remove();
  }
}

// Clear browsing history
function clearHistory() {
  if (confirm('Are you sure you want to clear your browsing history? This cannot be undone.')) {
    chrome.history.deleteAll(function() {
      const historyContainer = document.getElementById('history-container');
      historyContainer.innerHTML = '<div class="empty-message">History has been cleared.</div>';
      showStatus('Browsing history cleared successfully!', 'success');
    });
  }
}

// Debounce function for search input
function debounce(func, wait) {
  let timeout;
  return function() {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
}

// Show status message
function showStatus(message, type) {
  const statusElement = document.getElementById('status-message');
  statusElement.textContent = message;
  statusElement.className = `status status-${type}`;
  statusElement.style.display = 'block';
  
  // Hide after 3 seconds
  setTimeout(() => {
    statusElement.style.display = 'none';
  }, 3000);
}

function formatTimeSpent(seconds) {
  if (!seconds || seconds <= 0) return '0s';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  
  let timeString = '';
  if (hours > 0) timeString += `${hours}h `;
  if (minutes > 0 || hours > 0) timeString += `${minutes}m `;
  timeString += `${remainingSeconds}s`;
  
  return timeString;
}

// Function to delete a blocklist item by index
function deleteBlocklistItem(index) {
  fetch(`http://localhost:1978/api/blocklist/${index}`, {
    method: 'DELETE'
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('Item deleted:', data);
    // Refresh the blocklist display after deletion
    loadBlocklist();
  })
  .catch(error => {
    console.error('Error deleting blocklist item:', error);
    alert('Failed to delete item. Please try again.');
  });
} 