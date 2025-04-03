// Import all the modules
importScripts('./blocklist.js');

// Global variables
const serverUrl = 'http://localhost:1978';
// Note: We're not declaring blocklist here since it's already declared in blocklist.js

// Initialize extension
chrome.runtime.onInstalled.addListener(function() {
  console.log('WebWatch Blocker extension installed');
  
  // Fetch blocklist
  fetchBlocklist();
});

// Initialize: set up listeners
function initialize() {
  console.log('WebWatch Blocker initializing...');
  
  // Use webNavigation to catch navigation events earlier
  chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    // Only check main frame navigations (not iframes, etc.)
    if (details.frameId !== 0) return;
    
    console.log('Navigation starting to:', details.url);
    const result = await isUrlBlocked(details.url);
    
    if (result.blocked) {
      console.log('Blocking URL:', details.url, 'Reason:', result.reason);
      
      // Cancel the navigation and redirect to blocked page
      redirectToBlockedPage(details.tabId, details.url, result.reason);
    }
  });
  
  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'getBlocklist') {
      sendResponse({ blocklist: blocklist });
    } else if (message.action === 'refreshBlocklist') {
      fetchBlocklist().then(() => {
        sendResponse({ success: true, blocklist: blocklist });
      });
      return true; // Required for async sendResponse
    }
  });
  
  console.log('WebWatch Blocker initialized');
}

// Start the extension
initialize();

function redirectToBlockedPage(tabId, blockedUrl, reason) {
  const redirectUrl = chrome.runtime.getURL('ui/blocked/blocked.html') +
    '?url=' + encodeURIComponent(blockedUrl) +
    '&reason=' + encodeURIComponent(reason || 'This site has been blocked');

  chrome.tabs.update(tabId, { url: redirectUrl });
}