import Vue from 'vue';
import createRouter from './router.js';
import App from './App.vue';

export function createApp ({ defaultData }) {
  const router = createRouter();
  const app = new Vue({
    router,
    provide: {
      defaultData
    },
    render: h => h(App)
  });

  return { app, router };
}
