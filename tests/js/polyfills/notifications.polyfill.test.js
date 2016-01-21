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

var sandbox = sinon.sandbox.create();

QUnit.module('notifications', {
    beforeEach: function () {
      this.close = sinon.spy();
      var Notification = sandbox.stub(self, 'Notification')
          .returns({close: this.close});
      var requestPermission = sandbox.stub(Notification, 'requestPermission')
          .callsArg(0)  // Deprecated callback.
          .returns(Promise.resolve());
    },
    afterEach: function() {
      sandbox.restore();
    }
});

QUnit.test('creates a minimal notification', function(assert) {
  var done = assert.async();
  var opts = {'type': 'basic'}
  chrome.notifications.create(opts, function() {
    assert.ok(Notification.calledOnce);
    done();
  });
});

QUnit.test('creates a notification with correct body', function(assert) {
  var done = assert.async();
  var opts = {'type': 'basic', 'message': 'méssage'}
  chrome.notifications.create(opts, function() {
    assert.equal(Notification.args[0][1].body, 'méssage');
    done();
  });
});

QUnit.test('creates a notification with correct title',
    function(assert) {
      var done = assert.async();
      var opts = {'type': 'basic', 'title': 'títle'}
      chrome.notifications.create(opts, function() {
        assert.equal(Notification.args[0][0], 'títle');
        done();
      });
    }
);

QUnit.test('creates a notification with correct ID', function(assert) {
  var done = assert.async();
  var opts = {'type': 'basic', 'title': 'títle'}
  chrome.notifications.create('íd', opts, function() {
    assert.equal(Notification.args[0][1].tag, 'íd');
    done();
  });
});

QUnit.test('create closes notifications with same ID', function(assert) {
  var done = assert.async();
  var close = this.close;
  chrome.notifications.create('íde', {'type': 'basic'}, function() {
    chrome.notifications.create('íde', {'type': 'basic'}, function() {
      assert.ok(close.calledOnce);
      done();
    });
  });
});

QUnit.test('create generates an ID if none is provided', function(assert) {
  var done = assert.async();
  var clear = sandbox.stub(chrome.notifications, 'clear');
  chrome.notifications.create({'type': 'basic'}, function() {
    assert.ok('tag' in Notification.args[0][1]);
    assert.equal(typeof Notification.args[0][1].tag, 'string');
    done();
  });
});

QUnit.test('create requests notification permissions', function(assert) {
  var done = assert.async();
  chrome.notifications.create({'type': 'basic'}, function() {
    assert.ok(Notification.requestPermission.calledOnce);
    done();
  });
});

QUnit.test('create appends the contextMessage to the body', function(assert) {
  var done = assert.async();
  chrome.notifications.create({'type': 'basic', 'message': 'hello',
                               'contextMessage': 'world'}, function() {
    assert.equal(Notification.args[0][1].body, 'hello\n\nworld');
    done();
  });
});

QUnit.test('create adds progress text for progress notifications',
  function(assert) {
    var done = assert.async();
    chrome.notifications.create({'type': 'progress', 'message': 'hello',
                                 'progress': 15}, function() {
      assert.equal(Notification.args[0][1].body, 'hello\n\nProgress: 15%');
      done();
    });
});

QUnit.test('create warns if an unsupported type is given', function(assert) {
  var done = assert.async();
  var warn = sandbox.stub(console, 'warn');
  chrome.notifications.create({'type': 'faketype'}, function() {
    assert.ok(warn.calledOnce);
    assert.equal(warn.args[0].join(' '),
        'Notification type faketype not supported. Falling back to basic.');
    done();
  });
});

QUnit.test('creates a notification with the correct icon',function(assert) {
    var done = assert.async();
    chrome.notifications.create({'type': 'basic', 'iconUrl': 'aURL'},
        function() {
          assert.equal(Notification.args[0][1].icon, 'aURL');
          done();
        }
    );
});

QUnit.test('passes false to callback if no notification cleared',
    function(assert) {
      var done = assert.async();
      chrome.notifications.clear('thisiddoesnotexist', function(success) {
        assert.notOk(success);
        done();
      });
    }
);

QUnit.test('passes true to callback if notification cleared', function(assert) {
  var done = assert.async();
  chrome.notifications.create('thisiddoesexist', {'type': 'basic'},
      function() {
        chrome.notifications.clear('thisiddoesexist', function(success) {
          assert.ok(success);
          done();
        });
      }
  );
});

QUnit.test('clear closes the notification', function(assert) {
  var done = assert.async();
  var close = this.close;
  chrome.notifications.create('closesid', {'type': 'basic'},
      function() {
        chrome.notifications.clear('closesid', function(success) {
          assert.ok(close.called);
          done();
        });
      }
  );
});

// QUnit.test('returns an empty object if there are no notifications')
// TODO(alger): Implement this test, pending some way of resetting internals

QUnit.test(
    'passes GRANTED to callback if granted permission', function(assert) {
      Notification.permission = 'granted';
      chrome.notifications.getPermissionLevel(function(level) {
        assert.equal(level, chrome.notifications.PermissionLevel.GRANTED);
      });
    }
);

QUnit.test(
    'passes DENIED to callback if denied permission', function(assert) {
      Notification.permission = 'denied';
      chrome.notifications.getPermissionLevel(function(level) {
        assert.equal(level, chrome.notifications.PermissionLevel.DENIED);
      });
    }
);

QUnit.test(
  'passes DENIED to callback if no permission set', function(assert) {
    Notification.permission = 'default';
    chrome.notifications.getPermissionLevel(function(level) {
      assert.equal(level, chrome.notifications.PermissionLevel.DENIED);
    });
  }
);

// TODO(alger): Add tests for onClicked event handler.
