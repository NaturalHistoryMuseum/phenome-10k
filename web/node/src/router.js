import Vue from 'vue';
import Router from 'vue-router';

Vue.use(Router);

export default () => {
  return new Router({
    mode: 'history',
    routes: [
      {
        path: '/scans',
        alias: '/library',
        component: () => import('./pages/scans/ScansLibrary'),
        name: 'scans_library',
      },
      {
        path: '/scans/:page(\\d+)',
        alias: '/library/:page(\\d+)',
        component: () => import('./pages/scans/ScansLibrary'),
        name: 'scans_library-paged',
      },
      {
        path: '/scans/manage-uploads',
        alias: '/library/manage-uploads',
        component: () => import('./pages/scans/ScansManage'),
        name: 'scans_manage',
      },
      {
        path: '/scans/manage-uploads/page/:page(\\d+)',
        alias: '/library/manage-uploads/page/:page(\\d+)',
        component: () => import('./pages/scans/ScansManage'),
        name: 'scans_manage-paged',
      },
      {
        path: '/scans/create',
        component: () => import('./pages/scans/ScanEdit'),
        name: 'scan_create',
      },

      {
        path: '/publications',
        alias: '/publication',
        component: () => import('./pages/publications/PublicationsLibrary'),
        name: 'publications_library',
      },
      {
        path: '/publications/page/:page(\\d+)',
        alias: '/publication/page/:page(\\d+)',
        component: () => import('./pages/publications/PublicationsLibrary'),
        name: 'publications_library-paged',
      },
      {
        path: '/publications/manage-publications',
        alias: '/publication/manage-publications',
        component: () => import('./pages/publications/PublicationsManage'),
        name: 'publications_manage',
      },
      {
        path: '/publications/manage-publications/page/:page(\\d+)',
        alias: '/publication/manage-publications/page/:page(\\d+)',
        component: () => import('./pages/publications/PublicationsManage'),
        name: 'publications_manage-paged',
      },
      {
        path: '/publications/create',
        alias: '/publication/create',
        component: () => import('./pages/publications/PublicationsEdit'),
        name: 'publications_create',
      },
      {
        path: '/publications/:id',
        alias: '/publication/:id',
        component: () => import('./pages/publications/PublicationsView'),
        name: 'publications_view',
      },
      {
        path: '/publications/:id/edit',
        alias: '/publication/:id/edit',
        component: () => import('./pages/publications/PublicationsEdit'),
        name: 'publications_edit',
      },
      {
        path: '/users',
        component: () => import('./pages/admin/Users'),
        name: 'users',
      },
      // these MUST go at the bottom so other routes take precedence
      {
        path: '/:id',
        component: () => import('./pages/scans/ScanView'),
        name: 'scan_view',
      },
      {
        path: '/:id/edit',
        component: () => import('./pages/scans/ScanEdit'),
        name: 'scan_edit',
      },
    ],
  });
};
