import { createApp } from './app'

const { app, router } = createApp({ defaultData: window.p10k_defaultData });

router.onReady(() => {
  app.$mount('#app')
});
