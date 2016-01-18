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

'use strict';

var sandbox = sinon.sandbox.create();

QUnit.module('tts', {
    beforeEach: function () {
    },
    afterEach: function() {
      sandbox.restore();
    }
});

QUnit.test('speaking with no options', function(assert) {
  var speak = sandbox.stub(speechSynthesis, 'speak');
  var text = 'hello world!';
  chrome.tts.speak(text);
  assert.ok(speak.calledOnce);
  assert.equal(speak.args[0][0].text, text);
});

QUnit.skip('speaking with specified, existing voiceName', function(assert) {
  var done = assert.async();
  var SpeechSynthesisUtterance = sandbox.stub(self, 'SpeechSynthesisUtterance');
  var voiceName = 'test_voice';
  var getVoices = sandbox.stub(speechSynthesis, 'getVoices')
      .returns([{'name': voiceName}]);
  var speak = sandbox.stub(speechSynthesis, 'speak');
  chrome.tts.speak('hello', {'voiceName': voiceName}, function() {
    assert.equal(speak.args[0][0].voice, voiceName);
    done();
  });
});

var options = {
  'lang': 'fr',
  'rate': 3,
  'volume': 0.5,
  'pitch': 0.5
};

for (var option in options) {
  var test = function(option, assert) {
    var done = assert.async();
    var speak = sandbox.stub(speechSynthesis, 'speak');
    var text = 'hello world!';
    var speak_options = {};
    speak_options[option] = options[option];
    chrome.tts.speak(text, speak_options, function() {
      assert.ok(speak.called);
      assert.equal(speak.args[0][0].text, text);
      assert.equal(speak.args[0][0][option], options[option],
        'correct ' + option + ' spoken');
      done();
    });
  }.bind(null, option);
  QUnit.test('speaking with specified ' + option, test);
}

QUnit.test('stop', function (assert) {
  var cancel = sandbox.stub(speechSynthesis, 'cancel');
  var resume = sandbox.stub(speechSynthesis, 'resume');
  chrome.tts.stop();
  // stop should stop current speaking *and* unpause speaking.
  assert.ok(cancel.called);
  assert.ok(resume.called);
});

QUnit.test('pause', function (assert) {
  var pause = sandbox.stub(speechSynthesis, 'pause');
  chrome.tts.pause();
  assert.ok(pause.called);
});

QUnit.test('resume', function(assert) {
  var resume = sandbox.stub(speechSynthesis, 'resume');
  chrome.tts.resume();
  assert.ok(resume.called);
});

QUnit.test('getVoices', function(assert) {
  var done = assert.async();

  var voiceList = [{
    'default': false,
    'lang': 'en-US',
    'localService': false,
    'name': 'Google US English',
    'voiceURI': 'Google US English',
  }];
  var expectedVoiceList = [
    new chrome.tts.TtsVoice('Google US English', 'en-US', null, true, null,
                            null)
  ];

  var getVoices = sandbox.stub(speechSynthesis, 'getVoices')
      .returns(voiceList);

  chrome.tts.getVoices(function(voices) {
    assert.deepEqual(voices, expectedVoiceList);
    done();
  });
});

// TODO(alger): Test isSpeaking.

// TODO(alger): Test onEvent.

// TODO(alger): Test error handling.
