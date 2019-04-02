export default (Router) => {
  return new Router({
    mode: 'history',
    routes: [
      { path: '/library', component: () => import('./components/library.mjs') },
      { path: '/library/create', component: () => import('./components/upload.mjs') },
      { path: '/:id/edit', component: () => import('./components/upload.mjs') }
    ]
  });
}
