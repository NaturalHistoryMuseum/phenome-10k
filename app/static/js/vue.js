import createRouter from './router.mjs';

Vue.use(VueRouter);

const router = createRouter(VueRouter);

const app = new Vue({
  provide: {
    csrf: window.csrf
  },
  name: 'root',
  router,
  template: '<router-view></router-view>'
});

app.$mount('#root');
