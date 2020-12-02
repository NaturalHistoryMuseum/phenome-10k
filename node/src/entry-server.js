import { createApp } from './app';

export default async ({ url, defaultData }) => {
  const { app, router } = createApp({ defaultData })

  router.push(url);

  await new Promise((res, rej) => router.onReady(res, rej));

  const matchedComponents = router.getMatchedComponents(url);

  if (matchedComponents.length === 0) {
    throw { message: 'Component not found', code: 404 };
  }

  return app
}
