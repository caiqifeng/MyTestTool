// Jest setup file
// Mock uni-app global objects
global.uni = {
  request: jest.fn(),
  showToast: jest.fn(),
  showModal: jest.fn(),
  navigateTo: jest.fn(),
};

// Set global Vue and Vue internal globals for @vue/test-utils browser build
global.Vue = require('vue');
global.VueCompilerDOM = require('@vue/compiler-dom');
global.VueServerRenderer = require('@vue/server-renderer');