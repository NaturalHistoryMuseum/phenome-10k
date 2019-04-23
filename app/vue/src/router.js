import Vue from 'vue';
import Router from 'vue-router';

Vue.use(Router);

export default () => {
  return new Router({
    mode: 'history',
    routes: [
      { path: '/library', component: () => import('./components/Library'), name: 'library' },
      { path: '/library/create', component: () => import('./components/Upload') },
      { path: '/:id', component: () => import('./components/ScanOrPublication'), name: 'scan-or-pub' },
      { path: '/:id/edit', component: () => import('./components/Upload') }
    ]
  });
}
