// Copyright 2016 Google Inc. All Rights Reserved.
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

// Configuration file for Karma.

module.exports = function(config) {
  config.set({
    basePath: '',
    frameworks: ['qunit', 'sinon'],
    files: [
      'src/js/caterpillar.js',
      'node_modules/platform/platform.js',
      'tests/test_app_minimal/app.info.js',
      'src/js/polyfills/*.polyfill.js',
      'tests/**/*.test.js'
    ],
    exclude: [
    ],
    preprocessors: {
    },
    reporters: ['progress'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    customLaunchers: {
      FirefoxDeveloperFlagged: {
        base: 'FirefoxDeveloper',
        prefs: {
          'media.webspeech.synth.enabled': true
        }
      }
    },
    browsers: ['Chrome', 'FirefoxDeveloperFlagged'],
    concurrency: Infinity,
    client: {
      captureConsole: true,
    },
    autoWatch: false,
    singleRun: true,
  })
}
