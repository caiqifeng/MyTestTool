// Simple test to check if mount works
console.log('Requiring @vue/test-utils...');
const testUtils = require('@vue/test-utils/dist/vue-test-utils.cjs.js');
console.log('testUtils:', Object.keys(testUtils));
const { mount } = testUtils;

test('simple mount test', () => {
  // Create a simple component
  const component = {
    template: '<div>Test</div>',
  };

  console.log('mount:', typeof mount);
  const wrapper = mount(component);
  expect(wrapper.text()).toBe('Test');
});