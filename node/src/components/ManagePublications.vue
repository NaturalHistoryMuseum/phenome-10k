<template>
  <div class="ManagePublications Content__subgrid">
    <h1 class="ManagePublications__title">Manage Publications</h1>
    <Search class="ManagePublications__search" name="q" v-model="q" />
    <div class="ManagePublications__sidebar">
      <router-link :class="getYearClass()" :to="{ name:'manage-publications' }">All</router-link>
      <router-link :class="getYearClass(pub_year)" v-for="pub_year of $route.meta.data.years" :to="{ name:'manage-publications', query: { pub_year } }" :key="pub_year">{{ pub_year }}</router-link>
    </div>
    <table class="ManagePublications__grid">
      <thead class="ManagePublications__grid-head">
        <tr>
          <th class="ManagePublications__year-header">Year</th>
          <th class="ManagePublications__name-header">Name of Publication</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="publication in $route.meta.data.publications" :key="publication.id">
          <td class="ManagePublications__year">{{ publication.pub_year }}</td>
          <td>
            <router-link class="ManagePublications__publication-link" :to="{ name: 'publication', params: { id: publication.url_slug || publication.id } }">{{ publication.title }}</router-link>
            <div class="ManagePublications__authors">{{ publication.authors }}</div>
          </td>
          <td class="ManagePublications__actions-col">
            <form method="post" class="ManagePublications__actions">
              <input type="hidden" name="id" :value="publication.id">
              <button name="action" :value="publication.published ? 'unpublish' : 'publish'"
                >{{ publication.published ? 'Unpublish' : 'Publish' }}</button>
              <router-link :to="{ name: 'edit-publication' , params: { id: publication.id } }">Edit</router-link>
              <button name="action" value="delete" @click="confirmDelete">Delete</button>
            </form>
            <div class="ManagePublications__files">
              No. of Files: <span class="ManagePublications__files-count">{{ publication.scans.length }}</span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <Pagination :page="page"
                :total="totalPages"
                :to="page => ({
                    name: 'manage-publications-page',
                    params: { page },
                    query: this.$route.query
                  })"
                class="ManagePublications__footer" />
  </div>
</template>

<style>
.ManagePublications {
  grid-column-start: 1;
  grid-column-end: 4;
  grid-template-areas: ".       .    title "
                       "sidebar grid grid  "
                       "sidebar .    footer"
                       "sidebar .    .     ";
}

.ManagePublications__title {
  grid-area: title;
}

.ManagePublications__sidebar {
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

.ManagePublications__year {
  display: block;
  text-align: center;
  color: inherit;
}

.ManagePublications__year--active {
  font-weight: bold;
}

.ManagePublications__grid {
  margin-left: 1px;
  grid-area: grid;
  border-collapse: collapse;
}

.ManagePublications__grid tr:nth-child(even) {
  background: #ebebeb;
}

.ManagePublications__grid-head {
  font-weight: bold;
  font-family: 'HelveticaNeueW02-75Bold', Arial, Helvetica, sans-serif;
  color: #333;
  text-transform: uppercase;
  font-size: 11px;
}

.ManagePublications__grid-head th {
  padding: 10px 0;
}

.ManagePublications__year-header {
  width: 160px;
}

.ManagePublications__name-header {
  text-align: left;
}

.ManagePublications__grid td {
  padding: 10px 0;
  vertical-align: top;
}

td.ManagePublications__year {
  font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
  font-size: 12px;
  font-weight: bold;
  color: #666;
  width: 160px;
  text-align: center;
  width: 160px;
}

.ManagePublications__publication-link {
  color: #096;
  font-size: 18px;
  font-family: 'Neo Sans W01', Arial, Helvetica, sans-serif;
  display: block;
}

.ManagePublications__publication-link::first-letter {
  text-transform: uppercase;
}

.ManagePublications__authors {
  font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
  font-size: 11px;
  margin: 5px 0 0;
}

.ManagePublications__actions {
  display: flex;
  justify-content: flex-end;
}

.ManagePublications__actions > * {
  appearance: none;
  border: none;
  background: transparent;
  font-size: 10px;
  color: #666;
  cursor: pointer;
  padding: 0 5px;
  font-family: "HelveticaNeueW01-55Roma", Helvetica, Arial, sans-serif;

  &:hover {
    text-decoration: underline;
  }

  &:not(:last-child) {
    border-right: 1px solid #666;
  }
}

.ManagePublications__actions-col {
  text-align: right;
}

.ManagePublications__files {
  color: #999;
  font-size: 11px;
  font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
  margin: 6px 9px 0 0;
}

.ManagePublications__files-count {
  color: #333;
  font-family: 'Neo Sans W01', Arial, Helvetica, sans-serif;
}

.ManagePublications__footer {
  margin-top: 50px;
  grid-area: footer;
}

.ManagePublications__search {
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
      if(!confirm('This action will permenently delete the record and all attachments.')) {
        e.preventDefault();
      }
    },
    /**
     * Generate the CSS class for a filter-by-year link
     */
    getYearClass(year) {
      return {
        'ManagePublications__year': true,
        'ManagePublications__year--active': this.$route.query.pub_year == year
      };
    }
  }
}
</script>
