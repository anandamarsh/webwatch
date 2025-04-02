// Import all the modules
importScripts(
  './blocklist.js',
  './tracking.js',
  './listeners.js'
);

// Global variables
let serverUrl = 'http://localhost:1978';
let monitoringEnabled = true;
let trackIncognito = false;
let trackLocal = true;
let blocklist = [];

// Global object to store active sessions
const activeSessions = {};

// Initialize extension
chrome.runtime.onInstalled.addListener(function() {
  console.log('WebWatch extension installed');
  
  // Load settings
  loadSettings();
  
  // Fetch blocklist
  fetchBlocklist();
});

// Load settings from storage
function loadSettings() {
  chrome.storage.sync.get({
    serverUrl: 'http://localhost:1978',
    monitoringEnabled: true,
    trackIncognito: false,
    trackLocal: true
  }, function(items) {
    serverUrl = items.serverUrl;
    monitoringEnabled = items.monitoringEnabled;
    trackIncognito = items.trackIncognito;
    trackLocal = items.trackLocal;
    console.log('Settings loaded:', items);
  });
}