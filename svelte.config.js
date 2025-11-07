import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),

  compilerOptions: {
    // 启用运行时检查
    dev: process.env.NODE_ENV !== 'production',
  },
};
