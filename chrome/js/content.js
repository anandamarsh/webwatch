// Basic content script
console.log('WebWatch content script loaded');

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'getPageInfo') {
    // Get basic page information
    const pageInfo = {
      title: document.title,
      url: window.location.href,
      domain: window.location.hostname
    };
    sendResponse(pageInfo);
  }
  return true;
}); 