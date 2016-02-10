// Copyright 2015 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * Generic service worker code.
 */

(function() {

'use strict';

/**
 * Performs a cache lookup on a request, ignoring GET parameters.
 *
 * @param {Cache} cache Cache to lookup the request in.
 * @param {Request} request Request to lookup.
 * @param {object=} opt_options Options to pass to Cache.match.
 * @returns {Promise}
 */
var matchIgnoreParams = function(cache, request, opt_options) {
  var paramIndex = request.url.indexOf('?');
  if (paramIndex !== -1)
    request = new Request(request.url.substring(0, paramIndex), request);

  return cache.match(request, opt_options);
};

/**
 * Service worker activation event handler.
 *
 * Deletes caches that aren't present in CACHES.
 *
 * @param {event} e Activation event.
 */
var onActivate = function(e) {
  // Delete old versions of caches.
  var currentCaches = Object.keys(CACHES).map(k => CACHES[k]);
  e.waitUntil(caches.keys().then(cacheNames => Promise.all(
    cacheNames.map(cache => {
      if (currentCaches.indexOf(cache) === -1)
        return caches.delete(cache);
    })
  )));
};
self.addEventListener('activate', onActivate);

/**
 * Service worker fetch event handler.
 *
 * Fetches resources from the cache if they are cached, or from the web if they
 * are not.
 *
 * @param {event} e Fetch event.
 * @return {response} Fetch response.
 */
var onFetch = function(e) {
  e.respondWith(caches.open(CACHES['app']).then(cache =>
    matchIgnoreParams(cache, e.request).then(response => {
      if (response)
        return response;

      // Cache miss, fetch from web.
      var fetchRequest = e.request.clone();
      var headers = new Headers({
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': 0
      });
      return fetch(fetchRequest, {'headers': headers});
    })
  ));
};
self.addEventListener('fetch', onFetch);

/**
 * Service worker install event handler.
 *
 * Pre-caches all files in CACHED_FILES.
 *
 * @param {event} e Install event.
 */
var onInstall = function(e) {
  e.waitUntil(
    caches.open(CACHES['app'])
          .then(cache => cache.addAll(CACHED_FILES)));
  console.debug('Installed service worker.');
};
self.addEventListener('install', onInstall);

}).call(this);
