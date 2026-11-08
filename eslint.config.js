import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import globals from 'globals'
import style from './tools/eslint-plugin-style/index.js'

const BANNED_SYNTAX = [
  { selector: 'WhileStatement', message: 'while запрещён: используйте map / filter / reduce' },
  { selector: 'DoWhileStatement', message: 'do-while запрещён: используйте map / filter / reduce' },
  { selector: 'BreakStatement', message: 'break запрещён: перепишите через предикаты' },
  { selector: 'ContinueStatement', message: 'continue запрещён: перепишите через filter' },
]

const STRICT_RULES = {
  'style/single-return': 'error',
  'max-statements': ['error', 2],
  'max-depth': ['error', 1],
  complexity: ['error', 5],
  'no-restricted-syntax': ['error', ...BANNED_SYNTAX],
  'no-else-return': 'error',
  'no-lonely-if': 'error',
  'prefer-const': 'error',
}

export default tseslint.config(
  { ignores: ['**/dist/**', '**/node_modules/**', '.tools/**', '.venv/**', '**/*.d.ts'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx,js,mjs}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: { ...globals.browser, ...globals.node },
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    plugins: { style },
    rules: {
      ...STRICT_RULES,
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'error',
    },
  },
  {
    files: ['packages/ui/src/hooks/**/*.ts', 'packages/ui/src/hooks/**/*.tsx'],
    rules: { 'max-statements': ['error', 3] },
  },
  {
    files: ['tools/**/*.js', '*.config.js', '**/vite.config.ts'],
    rules: { 'max-statements': 'off', 'no-restricted-syntax': 'off', 'style/single-return': 'off', complexity: 'off', 'max-depth': 'off' },
  }
)
