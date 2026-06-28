import tseslint from "typescript-eslint";

const eslintConfig = [
  {
    ignores: [".next/**", "coverage/**", "node_modules/**", "next-env.d.ts"],
  },
  ...tseslint.configs.recommended,
];

export default eslintConfig;
