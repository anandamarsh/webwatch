// This script runs on all web pages
console.log('WebWatch Blocker content script loaded');

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'blockPage') {
    // Redirect to the blocked page
    window.location.href = chrome.runtime.getURL('ui/blocked/blocked.html') + 
      '?url=' + encodeURIComponent(window.location.href) + 
      '&reason=' + encodeURIComponent(message.reason || 'This website is blocked');
    
    sendResponse({ success: true });
  }
}); 