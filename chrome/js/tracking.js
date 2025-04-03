// Function to check if a URL should be tracked
function shouldTrackUrl(url) {
    try {
      const urlObj = new URL(url);
      
      // Skip chrome:// and chrome-extension:// URLs
      if (urlObj.protocol === 'chrome:' || urlObj.protocol === 'chrome-extension:') {
        return false;
      }
      
      // Skip localhost URLs
      if (urlObj.hostname === 'localhost' || urlObj.hostname === '127.0.0.1') {
        console.log('Skipping localhost URL:', url);
        return false;
      }
      
      // Skip about:blank and similar
      if (urlObj.protocol === 'about:') {
        return false;
      }
      
      return true;
    } catch (e) {
      console.error('Invalid URL:', url);
      return false;
    }
  }
  
  // Track page visit
  async function trackPageVisit(tab) {
    try {
      // Check if we should track this URL
      if (!shouldTrackUrl(tab.url)) {
        console.log('Skipping tracking for URL:', tab.url);
        return;
      }
      
      // Get server URL from settings
      const settings = await new Promise((resolve) => {
        chrome.storage.sync.get({
          serverUrl: 'http://localhost:1978'
        }, function(items) {
          resolve(items);
        });
      });
      
      // Get the page content
      let content = '';
      
      // Check if we can access the tab content
      if (tab.url && !tab.url.startsWith('chrome://') && !tab.url.startsWith('chrome-extension://')) {
        try {
          // Try to get content using the available API
          if (typeof chrome.scripting !== 'undefined') {
            // For Manifest V3, use chrome.scripting API with improved page load detection
            console.log('Using chrome.scripting API to get content');
            const results = await chrome.scripting.executeScript({
              target: { tabId: tab.id },
              func: async () => {
                function waitForPageLoad() {
                  return new Promise((resolve) => {
                    if (document.readyState === 'complete') {
                      resolve();
                    } else {
                      window.addEventListener('load', () => resolve(), { once: true });
                    }
                  });
                }

                function waitForDomToSettle(timeout = 2000) {
                  return new Promise(resolve => setTimeout(resolve, timeout));
                }

                await waitForPageLoad();
                await waitForDomToSettle(); // Give extra time for JS DOM changes

                return document.documentElement.outerHTML;
              }
            });
            
            if (results && results[0] && results[0].result) {
              content = results[0].result;
            }
          } else if (typeof chrome.tabs.executeScript !== 'undefined') {
            // For Manifest V2, use chrome.tabs.executeScript
            console.log('Using chrome.tabs.executeScript API to get content');
            const results = await new Promise((resolve) => {
              chrome.tabs.executeScript(tab.id, {
                code: `
                  (function() {
                    if (document.readyState === 'complete') {
                      return document.documentElement.outerHTML;
                    } else {
                      // If not complete, we can't use async/await in this context
                      // so we'll just return what we have
                      return document.documentElement.outerHTML;
                    }
                  })()
                `
              }, (results) => {
                resolve(results);
              });
            });
            
            if (results && results[0]) {
              content = results[0];
            }
          } else {
            console.warn('No content extraction API available');
          }
        } catch (e) {
          console.error(`Error getting content for ${tab.url}:`, e);
        }
      }
      
      // Send the visit data with whatever content we were able to get
      sendVisitData(tab, settings.serverUrl, content);
      
    } catch (error) {
      console.error('Error in trackPageVisit:', error);
    }
  }
  
  
  // Function to send visit data to the server
  function sendVisitData(tab, serverUrl, content) {
    // Prepare visit data
    const visitData = {
      url: tab.url,
      title: tab.title || '',
      content: content,
      timestamp: new Date().toISOString(),
      incognito: tab.incognito || false
    };
    
    console.log('Tracking page visit:', visitData.url);
    
    // Send to server
    fetch(`${serverUrl}/api/visits`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(visitData)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Visit tracked successfully:', data);
    })
    .catch(error => {
      console.error('Error tracking visit:', error);
    });
  }