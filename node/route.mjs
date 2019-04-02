// Step 1: Create a Vue instance
import Vue from 'vue'
import Router from 'vue-router'
import SSR from  'vue-server-renderer'
import createRouter from '../app/static/js/router'

Vue.use(Router);

const resolve = object => (object.call ? object() : object);

const router = createRouter(Router);
const [Page] = router.getMatchedComponents('/' + process.argv[2]);
const csrf = process.argv[3];

resolve(Page).then(({ default: Page }) => {
  const scripts = Page.scripts || [];

  const app = new Vue({
    data() {
      return { scripts };
    },
    provide: {
      csrf
    },
    components: {
      Page
    },
    template: `<body>
    <div id="root"><Page :csrf="csrf" /></div>
    <script src="https://unpkg.com/vue/dist/vue.js"></script>
    <script src="https://unpkg.com/vue-router/dist/vue-router.js"></script>
    <script src="/static/js/vue.js" type="module"></script>
    <script v-for="script in scripts" :src="script"></script>
    </body>`
  });

  // Step 2: Create a renderer
  const renderer = SSR.createRenderer()

  // in 2.5.0+, returns a Promise if no callback is passed:
  renderer.renderToString(app).then(html => {
    process.stdout.write(
      `<!DOCTYPE html><script>window.csrf = ${JSON.stringify(csrf)};</script>${html}`)
  }).catch(err => {
    console.log(err);
  })
});
