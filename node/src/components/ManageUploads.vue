<template>
  <div class="ManageUploads Content__subgrid">
    <h1 class="ManageUploads__title">Manage Uploads</h1>
    <Search class="ManageUploads__search" v-model="q" name="q" />
    <div class="ManageUploads__sidebar">
      <router-link :class="getLetterClass()" :to="{ name:'manage-uploads' }">All</router-link>
      <router-link :class="getLetterClass(char)" v-for="char of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" :to="{ name:'manage-uploads', query: { char } }" :key="char">{{ char }}</router-link>
    </div>
    <table class="ManageUploads__grid">
      <thead class="ManageUploads__grid-head">
        <tr>
          <th>Upload Date</th>
          <th class="ManageUploads__name-header">Name of Specimen</th>
          <th class="ManageUploads__name-header">Name of Uploader</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="scan in $route.meta.data.scans" :key="scan.id">
          <td class="ManageUploads__upload-date">{{ getDateCreated(scan) }}</td>
          <td>
            <router-link class="ManageUploads__scan-link" :to="{ name: 'scan', params: { id: scan.url_slug || scan.id } }">{{ scan.scientific_name || '(unnamed specimen)' }}</router-link>
            <dl class="ManageUploads__details">
              <template v-for="({ name, values }, ix) in getScanData(scan)"><!--
            --><template v-if="ix > 0">, </template>
                <dt :key="name">{{ name }}</dt>: <dd :key="name + '-val'">{{ values.join(', ') }}</dd><!--
          --></template>
            </dl>
          </td>
          <td>
            {{ scan.author }}
          </td>
          <td>
            <form method="post" class="ManageUploads__actions">
              <input name="csrf_token" type="hidden" :value="$route.meta.data.csrf_token">
              <button
                :formaction="$router.resolve({ name: 'edit-scan', params: { id: scan.id }, query: { redirect: $route.fullPath } }).href"
                :name="scan.published ? null : 'published'" value="On"
                >{{ scan.published ? 'Unpublish' : 'Publish' }}</button>
              <router-link :to="{ name: 'edit-scan' , params: { id: scan.id } }">Edit</router-link>
              <button name="delete" :value="scan.id" @click="confirmDelete">Delete</button>
            </form>
          </td>
        </tr>
      </tbody>
    </table>
    <Pagination :page="page"
                :total="totalPages"
                :to="page => ({
                    name: 'manage-uploads-page',
                    params: { page },
                    query: this.$route.query
                  })"
                class="ManageUploads__footer" />
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
}

.ManageUploads__search {
  grid-area: title;
  align-self: end;
  justify-self: end;
}
</style>


<script>
import Pagination from './Pagination';
import Search from './forms/Search';

export default {
  components: {
    Pagination,
    Search
  },
  data(){
    return {
      q: this.$route.meta.data.q
    }
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
    /**
     * Ask the user to confirm whether they want to delete the record, prevent form sub if not
     * @param e {Event} The form submit event
     */
    confirmDelete(e){
      if(!confirm('This action will permenently delete the source file and all attachments.')) {
        e.preventDefault();
      }
    },
    /**
     * Generate human readable creation date for a scan
     */
    getDateCreated(scan){
      const date = new Date(scan.created);
      const pad = n => String(n).padStart(2, '0')

      return `${pad(date.getDay())}.${pad(date.getMonth()+1)}.${date.getFullYear()}`;
    },
    /**
     * Generate an array of objects containing scan data item
     */
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
    /**
     * Generate the CSS class for a filter-by-letter link
     */
    getLetterClass(letter) {
      return {
        'ManageUploads__letter': true,
        'ManageUploads__letter--active': this.$route.query.char === letter
      };
    }
  }
}
</script>
