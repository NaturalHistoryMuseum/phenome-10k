// Step 1: Create a Vue instance
import Vue from 'vue'
import Router from 'vue-router'
import SSR from  'vue-server-renderer'
import createRouter from '../app/static/js/router'

Vue.use(Router);

const resolve = object => (object.call ? object() : object);

const path = '/' + process.argv[2];
const router = createRouter(Router);
const [Page] = router.getMatchedComponents(path);
const defaultJson = process.argv[3];
const defaultData = JSON.parse(defaultJson);

resolve(Page).then(async ({ default: Page }) => {
  const scripts = Page.scripts || [];
  const css = Page.css || [];

  const app = new Vue({
    router,
    data() {
      return { scripts, css };
    },
    provide: {
      defaultData
    },
    components: {
      Page
    },
    template: `<body>
    <link v-for="sheet in css" rel="stylesheet" :href="sheet" />
    <div id="root"><router-view /></div>
    <script src="https://unpkg.com/vue/dist/vue.js"></script>
    <script src="https://unpkg.com/vue-router/dist/vue-router.js"></script>
    <script src="/static/js/vue.js" type="module"></script>
    <script v-for="script in scripts" :src="script"></script>
    </body>`
  });

  router.push(path);

  await new Promise((res, rej) => router.onReady(res, rej));

  // Step 2: Create a renderer
  const renderer = SSR.createRenderer()

  // in 2.5.0+, returns a Promise if no callback is passed:
  return renderer.renderToString(app).then(html => {
    process.stdout.write(
      `<script>window.p10k_defaultData = ${defaultJson};</script>${html}`)
  })
}).catch(err => {
  console.error(err.stack);
  process.exit(1);
});
