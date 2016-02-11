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
 * Polyfill for the Chrome Apps TTS API.
 */

'use strict';

(function() {

if (!chrome.tts)
  chrome.tts = {};

/**
 * An event from the TTS engine to communicate the status of an utterance.
 */
chrome.tts.TtsEvent = class {
  /**
   * @param {string} type The type can be 'start' as soon as speech has started,
   *     'word' when a word boundary is reached, 'sentence' when a sentence
   *     boundary is reached, 'marker' when an SSML mark element is reached,
   *     'end' when the end of the utterance is reached, 'end' when the end of
   *     the utterance is reached, 'interrupted' when the utterance is stopped
   *     or interrupted before reaching the end, 'cancelled' when it's removed
   *     from the queue before ever being synthesized, or 'error' when any other
   *     error occurs. When pausing speech, a 'pause' event is fired if a
   *     particular utterance is paused in the middle, and 'resume' if an
   *     utterance resumes speech. Note that pause and resume events may not
   *     fire if speech is paused in-between utterances.
   * @param {double=} opt_charIndex The index of the current character in the
   *     utterance.
   * @param {string=} opt_errorMessage The error description, if the event type
   *     is 'error'.
   */ 
  constructor(type, opt_charIndex, opt_errorMessage) {
    this.type = type;
    this.charIndex = opt_charIndex;
    this.errorMessage = opt_errorMessage;
  }
};

/**
 * A description of a voice available for speech synthesis.
 */
chrome.tts.TtsVoice = class {
  /**
   * @param {string=} opt_voiceName The name of the voice.
   * @param {string=} opt_lang The language that this voice supports, in the
   *     form *language-region*. Examples: 'en', 'en-US', 'en-GB', 'zh-CN'.
   * @param {string=} opt_gender This voice's gender.
   * @param {bool=} opt_remote If true, the synthesis engine is a remote
   *     network resource.
   * @param {string=} opt_extensionId The ID of the extension providing this
   *     voice.
   * @param {string[]=} opt_eventTypes All of the callback event types that
   *     this voice is capable of sending.
   */
  constructor(opt_voiceName, opt_lang, opt_gender, opt_remote, opt_extensionId,
              opt_eventTypes) {
    this.voiceName = opt_voiceName;
    this.lang = opt_lang;
    this.gender = opt_gender;
    this.remote = opt_remote;
    this.extensionId = opt_extensionId;
    this.eventTypes = opt_eventTypes;
  }
};

/**
 * Speaks text using a text-to-speech engine.
 *
 * @param {string} utterance The text to speak.
 * @param {object=} opt_options The speech options.
 * @param {boolean=} opt_options.enqueue=false If true, enqueues this utterance
 *     if TTS is already in progress. If false, interrupts any current speech
 *     and flushes the speech queue before speaking this new utterance.
 * @param {string=} opt_options.voiceName The name of the voice to use for
 *     synthesis. If empty, uses any available voice.
 * @param {string=} opt_options.lang The language to be used for synthesis, in
 *     the form *language-region*. Examples: 'en', 'en-US', 'zh-CN'.
 * @param {double=} opt_options.rate=1.0 Speaking rate relative to the default
 *     rate of this voice. Must be in range [0.1, 10.0].
 * @param {double=} opt_options.pitch=1.0 Speaking pitch in range [0.0, 2.0].
 *     0.0 is lowest, 2.0 is highest.
 * @param {function=} opt_options.onEvent This function is called with events
 *     that occur in the process of speaking the utterance. The input parameter
 *     will be of type TtsEvent.
 * @param {function=} opt_callback Called right away, before speech finishes.
 */
chrome.tts.speak = function(utterance, opt_options, opt_callback) {
  // Juggle arguments.
  if (!(opt_options && opt_callback) && (typeof opt_options === 'function')) {
    opt_callback = opt_options;
    opt_options = undefined;
  }
  var msg = new SpeechSynthesisUtterance(utterance);

  // enqueue option.
  // CA default is to interrupt.
  if (opt_options && !opt_options.enqueue) {
    speechSynthesis.cancel();
  }

  // voiceName option.
  // If no voice matching the name is found, an arbitrary voice will be used.
  if (opt_options && opt_options.voiceName) {
    var voices = speechSynthesis.getVoices();
    var voice = voices.filter(voice => voice.name === opt_options.voiceName)[0];
    if (!voice) {
      console.warn('SpeechSynthesisVoice "' + opt_options.voiceName +
                   '" not found.');
    }
    msg.voice = voice;
  }

  // lang option.
  if (opt_options && opt_options.lang) {
    msg.lang = opt_options.lang;
  }

  // rate option.
  if (opt_options && opt_options.rate) {
    msg.rate = opt_options.rate;
  }

  // volume option.
  if (opt_options && opt_options.volume) {
    msg.volume = opt_options.volume;
  }

  // pitch option.
  if (opt_options && opt_options.pitch) {
    msg.pitch = opt_options.pitch;
  }

  // onEvent option.
  if (opt_options && opt_options.onEvent) {
    var events = ['start', 'end', 'error', 'pause', 'resume', 'mark',
                  'boundary'];
    for (var i = 0; i < events.length; i++) {
      var wrappedHandler = function(event) {
        // We need to convert SpeechSynthesisEvents into TtsEvents.

        // Types:
        // start -> start
        // end -> end
        // error -> error
        // pause -> pause
        // resume -> resume
        // mark -> marker
        // boundary -> word || sentence
  
        var type = event.type;
        if (type === 'mark') {
          type = 'marker';
        } else if (type === 'boundary') {
          // Two kinds of boundary: word and sentence.
          // The spec defines the name attribute of these events as either word
          // or sentence, so we can just use that.
          type = event.name;
        }

        // charIndex:
        var charIndex = event.charIndex;

        // error:
        // event.error is only defined if the event is an error.
        var error = event.error;

        // Construct the TtsEvent and call the event handler on it.
        var ttsEvent = new chrome.tts.TtsEvent(type, charIndex, error);
        opt_options.onEvent(ttsEvent);
      }
      msg.addEventListener(events[i], wrappedHandler);
    }
  }

  // Errors need to be caught and stored in chrome.runtime.lastError.
  msg.addEventListener('error', function(event) {
    caterpillar_.setError('Error speaking: ' + event.error);
  });

  speechSynthesis.speak(msg);

  // callback option.
  if (opt_callback)
    opt_callback();
};

/**
 * Stops any current speech and flushes the queue of any pending utterances.
 * In addition, if speech was paused, it will now be un-paused for the next call
 * to speak.
 */
chrome.tts.stop = function() {
  speechSynthesis.cancel();
  speechSynthesis.resume();
};

/**
 * Pauses speech synthesis, potentially in the middle of an utterance.
 * A call to resume or stop will un-pause speech.
 */
chrome.tts.pause = function() {
  speechSynthesis.pause();
};

/**
 * If speech was paused, resumes speaking where it left off.
 */
chrome.tts.resume = function() {
  speechSynthesis.resume();
};

/**
 * Checks whether the engine is currently speaking.
 *
 * @param {function=} opt_callback Callback function taking a boolean of whether
 *     or not the speech engine is currently speaking.
 */
chrome.tts.isSpeaking = function(opt_callback) {
  if (opt_callback)
    opt_callback(speechSynthesis.speaking);
};

/**
 * Convert a SpeechSynthesisVoice into a TtsVoice.
 *
 * @param {SpeechSynthesisVoice} voice Voice to convert.
 *
 * @returns chrome.tts.TtsVoice
 */
var toTtsVoice = function(voice) {
  return new chrome.tts.TtsVoice(voice.name, voice.lang, null,
                                 !voice.localService, null, null);
};

/**
 * Gets an array of all available voices.
 *
 * @param {function=} opt_callback Callback function taking an array of
 *     TtsVoices.
 */
chrome.tts.getVoices = function(opt_callback) {
  // SpeechSynthesis and CA TTS use different types for voices, so we need to
  // wrap the SpeechSynthesis types with CA TTS types.
  var voices = speechSynthesis.getVoices().map(toTtsVoice);
  if (opt_callback)
    opt_callback(voices);
};

}).call(this);
