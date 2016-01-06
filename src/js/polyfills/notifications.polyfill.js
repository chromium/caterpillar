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
 * Polyfill for Chrome Apps' notifications API.
 */

/**
 * Differences between the CA API and the polyfill.
 *
 * Missing functionality:
 *   NotificationOptions.appIconMaskUrl is ignored
 *   NotificationOptions.priority is ignored
 *   NotificationOptions.buttons is ignored
 *   NotificationOptions.imageUrl is ignored
 *   NotificationOptions.items is ignored
 *   NotificationOptions.isClickable is ignored
 *   NotificationOptions.contextMessage is used but not differentiated from the
 *     message itself.
 *   List and image notifications are not available
 *   Buttons cannot be placed on notifications
 *   Progress bars have been replaced with progress percentages of the form
 *     Progress: x%
 */

'use strict';

// Set up a namespace for the polyfill if necessary.
if (!chrome.notifications) chrome.notifications = {};

(function() {

// Private object to map notification IDs to their notification.
var notifications = {};

// List of event handlers for the click event.
var onClickHandlers = [];

// Arbitrary maximum for randomly generated notification IDs.
var MAX_NOTIFICATION_ID = 1000000;

/**
 * Represents the different types of notification that can be created.
 */
chrome.notifications.TemplateType = {
  BASIC: 'basic',
  LIST: 'list',
  IMAGE: 'image',
  PROGRESS: 'progress',
};

/**
 * Represents the different permission levels the app may have.
 */
chrome.notifications.PermissionLevel = {
  GRANTED: 'granted',
  DENIED: 'denied'
};

/**
 * Describes the contents of a notification.
 */
chrome.notifications.NotificationOptions = class {
  /**
   * @param {TemplateType=} type
   * @param {string=} iconUrl
   * @param {string=} appIconMaskUrl
   * @param {string=} title
   * @param {string=} message
   * @param {string=} contextMessage
   * @param {integer=} priority
   * @param {double=} eventTime
   * @param {object[]=} buttons
   * @param {string=} imageUrl
   * @param {object[]=} items
   * @param {integer=} progress
   * @param {boolean=} isClickable
   */
  constructor(type, iconUrl, appIconMaskUrl, title, message, contextMessage,
              priority, eventTime, buttons, imageUrl, items, progress,
              isClickable) {
    this.type = type;
    this.iconUrl = iconUrl;
    this.appIconMaskUrl = appIconMaskUrl;
    this.title = title;
    this.message = message;
    this.contextMessage = contextMessage;
    this.priority = priority;
    this.eventTime = eventTime;
    this.buttons = buttons;
    this.imageUrl = imageUrl;
    this.items = items;
    this.progress = progress;
    this.isClickable = isClickable;
  }
};

/**
 * Creates and displays a notification.
 *
 * @param {string=} opt_notificationId Identifier of the notification. If not
 *     specified, one will be randomly generated. If the notification ID matches
 *     an existing notification ID, this method will clear that notification
 *     before displaying a new notification.
 * @param {chrome.notifications.NotificationOptions} options Contents of the
 *     notification.
 * @param {function=} opt_callback Takes the notification ID that represents
 *     the notification.
 */
chrome.notifications.create = function(opt_notificationId, options,
                                       opt_callback) {
  // Juggle arguments.
  if (typeof opt_notificationId !== 'string') {
    opt_callback = options;
    options = opt_notificationId;
    opt_notificationId = undefined;
  }

  // If we have a notification ID and it matches an existing notification,
  // clear that notification first.
  if (opt_notificationId !== undefined && opt_notificationId in notifications) {
    // clear is asynchronous in Chrome Apps API, but this polyfill implements it
    // synchronously,
    chrome.notifications.clear(opt_notificationId);
  }

  // Generate a notification ID if necessary.
  if (opt_notificationId === undefined) {
    // Math.random is notoriously bad at random numbers, but we don't care very
    // much about collisions.
    opt_notificationId = Math.round(Math.random() * MAX_NOTIFICATION_ID);
  }

  // TODO(alger): Make this work in Firefox.
  Notification.requestPermission().then(() => {
    var title = options.title;
    var body = options.message;
    if (options.contextMessage)
      body += '\n\n' + options.contextMessage;
    if (options.type === chrome.notifications.TemplateType.PROGRESS) {
      body += '\n\nProgress: ' + options.progress + '%';
    } else if (options.type !== chrome.notifications.TemplateType.BASIC) {
      console.warn('Notification type', options.type, 'not supported.',
                   'Falling back to basic.');
    }
    var notification_options = {
      'body': body,
      'tag': opt_notificationId,
      'icon': options.iconUrl,
      'data': options,
    };

    var notification = new Notification(title, notification_options);

    for (var i = 0; i < onClickHandlers.length; i++) {
      notification.addEventListener('click', onClickHandlers[i]);
    }

    notifications[opt_notificationId] = notification;

    if (opt_callback)
      opt_callback(opt_notificationId);
  });
};

/**
 * Clears the specified notification.
 *
 * @param {string} notificationId
 * @param {function} opt_callback Takes a boolean which is true iff the
 *     notification was cleared successfully.
 */
chrome.notifications.clear = function(notificationId, opt_callback) {
  if (!(notificationId in notifications) && opt_callback) {
    opt_callback(false);
    return;
  }

  notifications[notificationId].close();
  delete notifications[notificationId];
  if (opt_callback)
    opt_callback(true);
};

/**
 * Retrieves all the notifications.
 *
 * @param {function} callback Function taking the object mapping notification ID
 *     to true.
 */
chrome.notifications.getAll = function(callback) {
  var notificationSet = {};
  for (var notificationId in notifications) {
    notificationSet[notificationId] = true;
  }
  callback(notificationSet);
};

/**
 * Retrieves whether the user has enabled notifications from this app.
 *
 * @param {function} callback Function taking a PermissionLevel as an argument.
 */
chrome.notifications.getPermissionLevel = function(callback) {
  if (Notification.permission === 'granted')
    callback(chrome.notifications.PermissionLevel.GRANTED);
  else
    callback(chrome.notifications.PermissionLevel.DENIED);
};

// TODO(alger): chrome.notifications.update

// TODO(alger): NotImplementedError for onClosed, onButtonClicked,
// onPermissionLevelChanged, onShowSettings

// Namespace.
chrome.notifications.onClicked = {};

/**
 * Adds an event handler for when the user clicks a notification.
 *
 * @param {function} callback Event handler taking notification ID as an
 *     argument.
 */
chrome.notifications.onClicked.addListener = function(callback) {
  var callbackWrapper = function(e) {
    callback(e.target.tag);
  };

  for (var i in notifications) {
    notifications[i].addEventListener('click', callbackWrapper);
  }

  onClickHandlers.push(callbackWrapper);
};

}).call(this);