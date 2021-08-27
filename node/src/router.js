import Vue from 'vue';
import Router from 'vue-router';

Vue.use(Router);

export default () => {
    return new Router({
        mode: 'history',
        routes: [
            { path: '/scans', alias: '/library', component: () => import('./components/Library'), name: 'library' },
            {
                path: '/scans/:page(\\d+)',
                alias: '/library/:page(\\d+)',
                component: () => import('./components/Library'),
                name: 'library-paged'
            },
            { path: '/scans/create', alias: '/library/create', component: () => import('./components/Upload') },
            {
                path: '/scans/manage-uploads',
                alias: '/library/manage-uploads',
                component: () => import('./components/ManageUploads'),
                name: 'manage-uploads'
            },
            {
                path: '/scans/manage-uploads/page/:page(\\d+)',
                alias: '/library/manage-uploads/page/:page(\\d+)',
                component: () => import('./components/ManageUploads'),
                name: 'manage-uploads-page'
            },
            { path: '/publications', component: () => import('./components/Publications'), name: 'publications' },
            {
                path: '/publications/create',
                component: () => import('./components/EditPublication'),
                name: 'create-publication'
            },
            {
                path: '/publications/page/:page(\\d+)',
                component: () => import('./components/Publications'),
                name: 'publications-paged'
            },
            {
                path: '/publications/manage-publications',
                component: () => import('./components/ManagePublications'),
                name: 'manage-publications'
            },
            {
                path: '/publications/manage-publications/page/:page(\\d+)',
                component: () => import('./components/ManagePublications'),
                name: 'manage-publications-page'
            },
            { path: '/publication/:id', component: () => import('./components/Publication'), name: 'publication' },
            {
                path: '/publication/:id/edit',
                component: () => import('./components/EditPublication'),
                name: 'edit-publication'
            },
            { path: '/users', component: () => import('./components/Users'), name: 'users' },
            { path: '/:id/edit', component: () => import('./components/Upload'), name: 'edit-scan' },
            { path: '/:id', component: () => import('./components/Scan'), name: 'scan' },
        ]
    });
}
