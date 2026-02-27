import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  {
    // useReactTable() triggers false positives for react-hooks/exhaustive-deps.
    // This is a known issue with TanStack Table — the hook manages its own
    // reactivity internally. We downgrade to "warn" project-wide so CI
    // doesn't fail on library false positives.
    rules: {
      "react-hooks/exhaustive-deps": "warn",
    },
  },
]);

export default eslintConfig;
