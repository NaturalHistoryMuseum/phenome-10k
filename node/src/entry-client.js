import { createApp } from './app'

const { app, router } = createApp({ defaultData: window.p10k_defaultData });

router.onReady(() => {
  app.$mount('#app')
});

// Whenever we navigate, try to get the JS data for the next page
router.beforeEach(async (to, from, next) => {
  const res = await fetch(to.fullPath, { headers: { accept: 'application/javascript' } });
  // Pass the data as `$route.meta.data` - the route is then responsible for finding this data
  to.meta.data = await res.json();
  next();
})
