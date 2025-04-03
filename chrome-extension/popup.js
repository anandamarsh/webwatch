document.addEventListener('DOMContentLoaded', function() {
  // UI Elements
  const blocklistElement = document.getElementById('blocklist');
  const loadingElement = document.getElementById('loading');
  const refreshButton = document.getElementById('refresh-btn');
  const statusValue = document.getElementById('status-value');
  const statusIndicator = document.getElementById('status-indicator');
  const blocklistCount = document.getElementById('blocklist-count');
  const emptyMessage = document.getElementById('empty-message');
  const noResults = document.getElementById('no-results');
  const searchInput = document.getElementById('search-input');
  const clearSearch = document.getElementById('clear-search');
  
  // Store the full blocklist
  let fullBlocklist = [];
  
  // Format date string
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  }
  
  // Render the blocklist
  function renderBlocklist(blocklist) {
    blocklistElement.innerHTML = '';
    
    if (blocklist.length === 0) {
      emptyMessage.style.display = 'block';
      noResults.style.display = 'none';
      blocklistCount.textContent = '0';
      return;
    }
    
    emptyMessage.style.display = 'none';
    noResults.style.display = 'none';
    blocklistCount.textContent = blocklist.length.toString();
    
    blocklist.forEach((entry, index) => {
      const li = document.createElement('li');
      
      // Format the URL for display
      let displayUrl = entry.url;
      if (entry.url.startsWith('domain:')) {
        displayUrl = entry.url.substring(7); // Remove 'domain:' prefix
      }
      
      li.innerHTML = `
        <div class="entry-url">${displayUrl}</div>
        <div class="entry-reason">${entry.reason || 'No reason provided'}</div>
      `;
      
      blocklistElement.appendChild(li);
    });
  }
  
  // Filter the blocklist based on search
  function filterBlocklist(searchTerm) {
    if (!searchTerm) {
      renderBlocklist(fullBlocklist);
      return;
    }
    
    const filtered = fullBlocklist.filter(entry => 
      entry.url.toLowerCase().includes(searchTerm.toLowerCase()) || 
      (entry.reason && entry.reason.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    
    if (filtered.length === 0) {
      blocklistElement.innerHTML = '';
      emptyMessage.style.display = 'none';
      noResults.style.display = 'block';
      blocklistCount.textContent = '0';
    } else {
      renderBlocklist(filtered);
    }
  }
  
  // Load and display the blocklist
  function loadBlocklist() {
    chrome.runtime.sendMessage({ action: 'getBlocklist' }, function(response) {
      loadingElement.style.display = 'none';
      
      if (response && response.blocklist) {
        fullBlocklist = response.blocklist;
        renderBlocklist(fullBlocklist);
      } else {
        statusValue.textContent = 'Error';
        statusIndicator.classList.add('error');
        emptyMessage.style.display = 'none';
        
        const errorLi = document.createElement('li');
        errorLi.className = 'error-item';
        errorLi.textContent = 'Failed to load blocklist';
        blocklistElement.appendChild(errorLi);
      }
    });
  }
  
  // Refresh the blocklist from the API
  refreshButton.addEventListener('click', function() {
    loadingElement.style.display = 'flex';
    blocklistElement.innerHTML = '';
    emptyMessage.style.display = 'none';
    noResults.style.display = 'none';
    statusValue.textContent = 'Refreshing...';
    statusIndicator.className = 'status-indicator refreshing';
    
    chrome.runtime.sendMessage({ action: 'refreshBlocklist' }, function(response) {
      loadingElement.style.display = 'none';
      
      if (response && response.success) {
        statusValue.textContent = 'Active';
        statusIndicator.className = 'status-indicator active';
        fullBlocklist = response.blocklist;
        renderBlocklist(fullBlocklist);
        
        // Clear search when refreshing
        searchInput.value = '';
      } else {
        statusValue.textContent = 'Error';
        statusIndicator.className = 'status-indicator error';
        
        const errorLi = document.createElement('li');
        errorLi.className = 'error-item';
        errorLi.textContent = 'Failed to refresh blocklist';
        blocklistElement.appendChild(errorLi);
      }
    });
  });
  
  // Search functionality
  searchInput.addEventListener('input', function() {
    filterBlocklist(this.value);
    clearSearch.style.display = this.value ? 'block' : 'none';
  });
  
  clearSearch.addEventListener('click', function() {
    searchInput.value = '';
    filterBlocklist('');
    this.style.display = 'none';
    searchInput.focus();
  });
  
  // Initial load
  statusIndicator.className = 'status-indicator active';
  loadBlocklist();
});