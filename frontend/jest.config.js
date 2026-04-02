module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  moduleFileExtensions: ['vue', 'js', 'ts', 'json'],
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.ts$': 'ts-jest',
    '^.+\\.js$': 'babel-jest',
  },
  transformIgnorePatterns: [
    'node_modules/(?!(vue|@vue|@vue/test-utils|@vue/vue3-jest|@vue/compiler-dom|@vue/compiler-sfc|@vue/server-renderer)/)',
  ],
  testMatch: ['**/__tests__/**/*.spec.[jt]s', '**/?(*.)+(spec|test).[jt]s'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@store/(.*)$': '<rootDir>/src/store/$1',
    '^@api/(.*)$': '<rootDir>/src/api/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@shared/(.*)$': '<rootDir>/../shared/src/$1',
    '^@vue/test-utils$': '<rootDir>/../../node_modules/@vue/test-utils/dist/vue-test-utils.cjs.js',
  },
  collectCoverage: true,
  collectCoverageFrom: [
    'src/components/**/*.{vue,ts,js}',
    '!src/**/*.d.ts',
  ],
  coverageReporters: ['text', 'lcov'],
  setupFiles: ['<rootDir>/jest.setup.js'],
  globals: {
    'vue-jest': {
      compiler: '@vue/compiler-dom',
    },
  },
};