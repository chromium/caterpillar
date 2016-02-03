// make a chrome app window
chrome.app.runtime.onLaunched.addListener(function() {
  chrome.app.window.create('ttstest.html', {
    id: 'id'
  });
});
