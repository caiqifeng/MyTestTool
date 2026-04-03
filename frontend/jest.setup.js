import { config } from '@vue/test-utils';

// 配置Vue Test Utils
config.global = {
  ...config.global,
  // 全局组件模拟（如果有的话）
  // 全局插件（如果有的话）
};

// 全局测试辅助函数
global.testUtils = {
  mountComponent: (component, options = {}) => {
    return mount(component, {
      global: {
        plugins: [], // 添加全局插件
        components: {}, // 添加全局组件
      },
      ...options,
    });
  },
};