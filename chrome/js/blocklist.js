// Check if monitoring is enabled
function isMonitoringEnabled() {
    return new Promise((resolve) => {
      chrome.storage.sync.get({
        monitoringEnabled: true
      }, function(items) {
        resolve(items.monitoringEnabled);
      });
    });
  }
  
  // Fetch blocklist from server
  async function fetchBlocklist() {
    try {
      // Get server URL from settings
      const url = await new Promise((resolve) => {
        chrome.storage.sync.get({
          serverUrl: 'http://localhost:1978'
        }, function(items) {
          resolve(items.serverUrl);
        });
      });
      
      console.log('Fetching blocklist from:', url);
      
      const response = await fetch(`${url}/api/blocklist`);
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      
      blocklist = await response.json();
      console.log('Blocklist loaded:', blocklist);
      return blocklist;
    } catch (error) {
      console.error('Error fetching blocklist:', error);
      return [];
    }
  }
  
  // Function to check if a URL is blocked
  async function isUrlBlocked(url) {
    // Always fetch the latest blocklist
    const blocklist = await fetchBlocklist();
    
    // Create URL object for easier domain extraction
    let urlObj;
    try {
      urlObj = new URL(url);
    } catch (e) {
      console.error('Invalid URL:', url);
      return { blocked: false };
    }
    
    // Extract the domain from the URL
    const domain = urlObj.hostname;
    console.log('Checking domain:', domain);
    
    for (const item of blocklist) {
      const blockedUrl = item.url;
      
      // Exact match
      if (url === blockedUrl) {
        console.log('Exact match found for:', url);
        return { blocked: true, reason: item.reason };
      }
      
      // Domain match (if blocked URL starts with domain:)
      if (blockedUrl.startsWith('domain:')) {
        const blockedDomain = blockedUrl.substring(7); // Remove 'domain:' prefix
        if (domain === blockedDomain || domain.endsWith('.' + blockedDomain)) {
          console.log('Domain match found for:', domain, 'with pattern:', blockedDomain);
          return { blocked: true, reason: item.reason };
        }
      }
      
      // Wildcard domain match (for *.example.com/* patterns)
      if (blockedUrl.startsWith('*.') && blockedUrl.includes('/*')) {
        const blockedDomain = blockedUrl.substring(2, blockedUrl.indexOf('/*'));
        if (domain === blockedDomain || domain.endsWith('.' + blockedDomain)) {
          console.log('Wildcard domain match found for:', domain, 'with pattern:', blockedDomain);
          return { blocked: true, reason: item.reason };
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
          console.log('Pattern match found for:', url, 'with pattern:', blockedUrl);
          return { blocked: true, reason: item.reason };
        }
        
        // Special case for domain wildcards
        if (blockedUrl.startsWith('*.')) {
          const blockedDomain = blockedUrl.substring(2);
          if (domain === blockedDomain || domain.endsWith('.' + blockedDomain)) {
            console.log('Domain wildcard match found for:', domain, 'with pattern:', blockedDomain);
            return { blocked: true, reason: item.reason };
          }
        }
      }
    }
    
    return { blocked: false };
  }