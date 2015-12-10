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
 * @file Common utilities and types for caterpillar.
 * @author alger@google.com
 */

'use strict';

// Set up a namespace if one doesn't already exist.
if (!chrome) chrome = {};
if (!chrome.caterpillar) chrome.caterpillar = {};

(function() {

/**
 * Enumeration of types that caterpillar Messages can be.
 */
chrome.caterpillar.MessageType = {
  // Internal communication for emulating notifications.
  NOTIFICATION: 'notification',
  // Internal communication for emulating runtime.sendMessage.
  BACKGROUND: 'background'
};

/**
 * Message sent between a webpage and its service worker as part of caterpillar
 * internals.
 */
chrome.caterpillar.Message = class {
  /**
   * @param {chrome.caterpillar.MessageType} type Type of message being sent.
   * @param {any[]} args Arguments to any functions called by the service
   *     worker as part of handling this message.
   * @param {function} callback Function to call after the message is handled.
   */
  constructor(type, args, callback) {
    this.type = type;
    this.args = args;
    this.callback = callback;
    this.caterpillar = true; // Identify this object as a caterpillar Message.
  }

  /**
   * @returns {string} A string representation of this message.
   */
  toString() {
    return 'chrome.caterpillar.Message(' + this.type + ', [...])';
  }

  /**
   * Convert a Chrome Apps background message into a Caterpillar Message.
   *
   * @param {any} message The message sent by the Chrome Apps API.
   * @param {function} callback Function called after caterpillar Message is
   *     handled.
   *
   * @returns {chrome.caterpillar.Message}
   */
  static fromBackgroundMessage(message, callback) {
    return new chrome.caterpillar.Message(
      chrome.caterpillar.MessageType.BACKGROUND, [message], callback);
  }
};

/**
 * Sets an error message in lastError if chrome.runtime is loaded.
 *
 * @param {string} message The error message to set.
 *
 * @throws Error with given message if runtime is not loaded, and a warning that
 *     runtime isn't loaded.
 */
chrome.caterpillar.setError = function(message) {
  if (!chrome.runtime) {
    console.warn('chrome.runtime not found; runtime errors may not be caught.');
    throw new Error(message);
  }
  chrome.runtime.lastError = { 'message': message };
};

}).call(this);