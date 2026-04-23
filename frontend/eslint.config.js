// eslint.config.js - ESLint v9 flat config format
import js from '@eslint/js';

export default [
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "module",
      globals: {
        console: "readonly",
        process: "readonly",
        require: "readonly",
        module: "readonly",
        __dirname: "readonly"
      }
    },
    rules: {
      "no-unused-vars": "warn",
      "semi": ["error", "always"],
      "no-console": "off"
    }
  }
];
