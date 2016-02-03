// make a chrome app window
// TODO(Caterpillar): Check usage of app.runtime.onLaunched.addListener.
chrome.app.runtime.onLaunched.addListener(function() {
// TODO(Caterpillar): Check usage of app.window.create.
  chrome.app.window.create('ttstest.html', {
    id: 'id'
  });
});
