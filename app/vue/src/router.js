import Vue from 'vue';
import Router from 'vue-router';

Vue.use(Router);

export default () => {
  return new Router({
    mode: 'history',
    routes: [
      { path: '/library', component: () => import('./components/Library'), name: 'library' },
      { path: '/library/create', component: () => import('./components/Upload') },
      { path: '/library/manage-uploads', component: () => import('./components/ManageUploads'), name: 'manage-uploads' },
      { path: '/library/manage-uploads/page/:page(\\d+)', component: () => import('./components/ManageUploads'), name: 'manage-uploads-page' },
      { path: '/publications', component: () => import('./components/Publications'), name: 'publications' },
      { path: '/publications/page/:page(\\d+)', component: () => import('./components/Publications'), name: 'publications-paged' },
      { path: '/:id', component: () => import('./components/ScanOrPublication'), name: 'scan-or-pub' },
      { path: '/:id/edit-scan', component: () => import('./components/Upload'), name: 'edit-scan' },
    ]
  });
}
