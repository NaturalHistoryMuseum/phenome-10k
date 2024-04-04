import Vue from 'vue';
import createRouter from './router.js';
import App from './App.vue';

export function createApp({ defaultData }) {
  const router = createRouter();

  router.onReady(() => {
    router.currentRoute.meta.data = defaultData;
  });

  const app = new Vue({
    router,
    render: (h) => h(App),
  });

  return { app, router };
}
