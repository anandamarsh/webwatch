// Listen for tab updates to check blocklist
chrome.tabs.onUpdated.addListener(async function(tabId, changeInfo, tab) {
    // Only check when the page has finished loading
    if (changeInfo.status === 'complete' && tab.url) {
      // Check if monitoring is enabled
      const monitoringEnabled = await isMonitoringEnabled();
      if (!monitoringEnabled) {
        console.log('Monitoring is disabled, skipping tab check');
        return;
      }
      
      // Skip chrome:// and chrome-extension:// URLs
      if (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://')) {
        return;
      }
      
      // Check if URL is blocked
      const blockCheck = await isUrlBlocked(tab.url);
      if (blockCheck.blocked) {
        console.log('Blocked URL:', tab.url, 'Reason:', blockCheck.reason);
        
        // Get the previous URL from tab history if available
        let previousUrl = '';
        try {
          // Try to get the previous URL from history
          chrome.tabs.executeScript(tabId, {
            code: 'document.referrer'
          }, function(results) {
            if (results && results[0]) {
              previousUrl = results[0];
            }
          });
        } catch (e) {
          console.log('Could not get referrer:', e);
        }
        
        // Create the redirect URL with properly encoded parameters
        const redirectUrl = chrome.runtime.getURL('ui/blocked/blocked.html') + 
          '?url=' + encodeURIComponent(tab.url) + 
          '&reason=' + encodeURIComponent(blockCheck.reason || 'This site has been blocked') +
          (previousUrl ? '&referrer=' + encodeURIComponent(previousUrl) : '');
        
        console.log('Redirecting to:', redirectUrl);
        
        // Redirect to blocked page
        chrome.tabs.update(tabId, { url: redirectUrl });
        return;
      }
      
      // Track the URL visit if it should be tracked
      if (shouldTrackUrl(tab.url)) {
        // Don't track incognito tabs unless enabled
        if (!tab.incognito || trackIncognito) {
          trackPageVisit(tab);
        }
      }
    }
  });
  
  // Listen for navigation events to check blocklist before page loads
  chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    // Only check main frame navigations
    if (details.frameId === 0) {
      // Check if monitoring is enabled
      const monitoringEnabled = await isMonitoringEnabled();
      if (!monitoringEnabled) {
        console.log('Monitoring is disabled, skipping navigation check');
        return;
      }
      
      // Skip the blocked.html page itself to avoid loops
      if (details.url.includes('blocked.html')) {
        return;
      }
      
      const checkResult = await isUrlBlocked(details.url);
      if (checkResult.blocked) {
        console.log('Blocked navigation to:', details.url, 'Reason:', checkResult.reason);
        
        // Create the redirect URL with properly encoded parameters
        const redirectUrl = chrome.runtime.getURL('ui/blocked/blocked.html') + 
          '?url=' + encodeURIComponent(details.url) + 
          '&reason=' + encodeURIComponent(checkResult.reason || 'This site has been blocked');
        
        console.log('Redirecting to:', redirectUrl);
        
        // Cancel the navigation and redirect to blocked page
        chrome.tabs.update(details.tabId, { url: redirectUrl });
      }
    }
  });
  
  // Listen for settings changes
  chrome.storage.onChanged.addListener(function(changes, namespace) {
    if (namespace === 'sync') {
      if (changes.serverUrl) {
        serverUrl = changes.serverUrl.newValue;
        console.log('Server URL updated:', serverUrl);
        
        // Refresh blocklist when server URL changes
        fetchBlocklist();
      }
      
      if (changes.monitoringEnabled) {
        monitoringEnabled = changes.monitoringEnabled.newValue;
        console.log('Monitoring enabled:', monitoringEnabled);
      }
      
      if (changes.trackIncognito) {
        trackIncognito = changes.trackIncognito.newValue;
        console.log('Track incognito:', trackIncognito);
      }
      
      if (changes.trackLocal) {
        trackLocal = changes.trackLocal.newValue;
        console.log('Track localhost:', trackLocal);
      }
    }
  });
  
  // Listen for messages from popup or options page
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'getBlocklist') {
      fetchBlocklist().then(blocklist => {
        sendResponse({ blocklist: blocklist });
      });
      return true; // Required for async sendResponse
    }
    
    if (request.action === 'checkBlocked') {
      isUrlBlocked(request.url).then(result => {
        sendResponse(result);
      });
      return true; // Required for async sendResponse
    }
    
    if (request.action === 'refreshSettings') {
      loadSettings();
      sendResponse({ success: true });
    }
  });