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
 * Stub for Chrome Apps' power API, so that calls to the API functions won't
 * stop apps from running due to errors.
 */

(function() {

'use strict';

// Set up a namespace for the stub if necessary.
if (!chrome.power)
  chrome.power = {};

/**
 * Describes the degree to which power management should be disabled.
 */
chrome.power.Level = {
  SYSTEM: 'system',
  DISPLAY: 'display'
};

/**
 * Requests that power management be temporarily disabled. Does nothing.
 *
 * @param {chrome.power.Level} Degree to which power management should be
 *     disabled.
 */
chrome.power.requestKeepAwake = function(level) {
};

/**
 * Releases a request previously made via requestKeepAwake(). Does nothing.
 */
chrome.power.releaseKeepAwake = function() {
};

}).call(this);
