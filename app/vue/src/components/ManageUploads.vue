<template>
  <div class="ManageUploads Subgrid">
    <h1 class="ManageUploads__title">Manage Uploads</h1>
    <div class="ManageUploads__sidebar">
      <router-link :class="getLetterClass()" :to="{ name:'manage-uploads' }">All</router-link>
      <router-link :class="getLetterClass(char)" v-for="char of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" :to="{ name:'manage-uploads', query: { char } }" :key="char">{{ char }}</router-link>
    </div>
    <table class="ManageUploads__grid">
      <thead class="ManageUploads__grid-head">
        <tr>
          <th>Upload Date</th>
          <th class="ManageUploads__name-header">Name of Specimen</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="scan in $route.meta.data.scans" :key="scan.id">
          <td class="ManageUploads__upload-date">{{ getDateCreated(scan) }}</td>
          <td>
            <router-link class="ManageUploads__scan-link" :to="{ name: 'scan-or-pub', params: { id: scan.url_slug || scan.id } }">{{ scan.scientific_name }}</router-link>
            <dl class="ManageUploads__details">
              <template v-for="({ name, values }, ix) in getScanData(scan)"><!--
            --><template v-if="ix > 0">, </template>
                <dt :key="name">{{ name }}</dt>: <dd :key="name + '-val'">{{ values.join(', ') }}</dd><!--
          --></template>
            </dl>
          </td>
          <td>
            <form method="post" class="ManageUploads__actions">
              <input name="csrf_token" type="hidden" :value="$route.meta.data.csrf_token">
              <button
                :formaction="$router.resolve({ name: 'edit-scan', params: { id: scan.id }, query: { redirect: $route.fullPath } }).href"
                :name="scan.published ? null : 'published'" value="On"
                >{{ scan.published ? 'Unpublish' : 'Publish' }}</button>
              <router-link :to="{ name: 'edit-scan' , params: { id: scan.id } }">Edit</router-link>
              <button name="delete" :value="scan.id">Delete</button>
            </form>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="ManageUploads__footer">
      <div>Page {{ page }} of {{ $route.meta.data.total_pages || 1 }}</div>
      <div v-if="$route.meta.data.total_pages > 1">
        <template v-if="page > 2">
          <Page page="1" /> …
        </template>
        <Page v-if="page > 1" :page="page - 1" />
        <Page :page="page" />
        <Page v-if="page < totalPages" :page="page + 1" />
        <template v-if="page < totalPages - 1">
          … <Page :page="totalPages" />
        </template>
      </div>
    </div>
  </div>
</template>

<style>
.ManageUploads {
  grid-column-start: 1;
  grid-column-end: 4;
  grid-template-areas: ".       .    title "
                       "sidebar grid grid  "
                       "sidebar .    footer"
                       "sidebar .    .     ";
}

.ManageUploads__title {
  color: #096;
  font-weight: normal;
  font-family: 'Neo Sans W01', Arial, Helvetica, sans-serif;
  font-size: 24px;
  margin: 40px 0 33px;
  grid-area: title;
}

.ManageUploads__sidebar {
  grid-area: sidebar;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin: 0 10px;
  text-transform: uppercase;
  font-size: 11px;
  font-family: 'HelveticaNeueW01-55Roma', Arial, Helvetica, sans-serif;
  color: #666;
  line-height: 17px;
}

.ManageUploads__letter {
  display: block;
  width: 2em;
  text-align: center;
  color: inherit;
}

.ManageUploads__letter--active {
  font-weight: bold;
}

.ManageUploads__grid {
  margin-left: 1px;
  grid-area: grid;
  border-collapse: collapse;
}

.ManageUploads__grid tr:nth-child(even) {
  background: #ebebeb;
}

.ManageUploads__grid-head {
  font-weight: bold;
  font-family: 'HelveticaNeueW02-75Bold', Arial, Helvetica, sans-serif;
  color: #333;
  text-transform: uppercase;
  font-size: 11px;
}

.ManageUploads__grid-head th {
  padding: 10px 0;
}

.ManageUploads__name-header {
  text-align: left;
}

.ManageUploads__grid td {
  padding: 10px 0;
  vertical-align: top;
}

td.ManageUploads__upload-date {
  font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
  font-size: 12px;
  font-weight: bold;
  color: #666;
  width: 160px;
  padding: 10px 40px;
}

.ManageUploads__scan-link {
  color: #096;
  font-size: 18px;
  font-family: 'Neo Sans W01', Arial, Helvetica, sans-serif;
  display: block;
}

.ManageUploads__scan-link::first-letter {
  text-transform: uppercase;
}

.ManageUploads__details {
  font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
  font-size: 11px;
  margin: 5px 0 0;
}

.ManageUploads__details > * {
  display: inline;
  margin: 0;
}

.ManageUploads__details dt {
  color: #999;
}

.ManageUploads__actions {
  display: flex;
  justify-content: flex-end;
}

.ManageUploads__actions > * {
  appearance: none;
  border: none;
  background: transparent;
  font-size: 10px;
  color: #666;
  cursor: pointer;
  padding: 0 5px;
  font-family: Helvetica, Arial, sans-serif;

  &:hover {
    text-decoration: underline;
  }

  &:not(:last-child) {
    border-right: 1px solid #666;
  }
}

.ManageUploads__footer {
  margin-top: 50px;
  grid-area: footer;
  display: flex;
  justify-content: space-between;
  font-family: 'HelveticaNeueW01-55Roma', Arial, Helvetica, sans-serif;
  font-size: 11px;
  color: #333;
}

.ManageUploads__page--active {
  color: #096;
}
</style>


<script>
const Page = {
  props: ['page'],
  render(h){
    return h('router-link', {
      attrs: {
        to: {
          name: 'manage-uploads-page',
          params: {
            page: this.page,
          },
          query: this.$route.query
        }
      },
      class: {
        "ManageUploads__page": true,
        "ManageUploads__page--active": this.$route.meta.data.page === this.page
      }
    }, [this.page]);
  }
}

export default {
  components: {
    Page
  },
  computed: {
    page() {
      return this.$route.meta.data.page
    },
    totalPages() {
      return this.$route.meta.data.total_pages;
    }
  },
  methods: {
    getDateCreated(scan){
      const date = new Date(scan.created);
      const pad = n => String(n).padStart(2, '0')

      return `${pad(date.getDay())}.${pad(date.getMonth())}.${date.getFullYear()}`;
    },
    getScanData(scan){
      const data = [];
      if (scan.specimen_id) {
        data.push({
          name: 'Specimen ID',
          values: [scan.specimen_id]
        })
      }

      const elements = scan.tags.filter(tag => tag.category === 'elements');
      if (elements.length > 0) {
        data.push({
          name: 'Elements',
          values: elements.map(el => el.name)
        })
      }

      return data;
    },

    getLetterClass(letter) {
      return {
        'ManageUploads__letter': true,
        'ManageUploads__letter--active': this.$route.query.char === letter
      };
    }
  }
}
</script>
