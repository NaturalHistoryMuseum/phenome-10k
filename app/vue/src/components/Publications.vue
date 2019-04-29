<template>
  <div class="Publications Subgrid">
    <h1 class="Publications__title">Publications</h1>
    <table class="Publications__grid">
      <thead class="Publications__grid-head">
        <tr>
          <th>Year</th>
          <th class="Publications__name-header">Name of Publication</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(pub, ix) in publications" :key="pub.id">
          <td class="Publications__year">
            {{ !publications[ix-1] || publications[ix-1].pub_year !== pub.pub_year ? pub.pub_year : '' }}
          </td>
          <td>
            <router-link class="Publications__link" :to="{ name: 'scan-or-pub', params: { id: pub.url_slug || pub.id } }">{{ pub.title }}</router-link>
            <div class="Publications__details">
              <div class="Publications__authors">
                {{ pub.authors }}
              </div>
              <div class="Publications__files">
                No. of Files: <span class="Publications__files-count">{{ pub.files.length }}</span>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <Pagination :page="$route.meta.data.page"
                :total="$route.meta.data.total_pages"
                :to="page => ({
                    name: 'publications-paged',
                    params: { page },
                    query: this.$route.query
                  })"
                class="Publications__footer" />
  </div>
</template>

<style>
.Publications {
  grid-column-start: 1;
  grid-column-end: 4;
  grid-template-areas: ".  .    title "
                       ".  grid grid  "
                       ".  .    footer"
                       ".  .    .     ";
}

.Publications__title {
  color: #096;
  font-weight: normal;
  font-family: 'Neo Sans W01', Arial, Helvetica, sans-serif;
  font-size: 24px;
  margin: 40px 0 33px;
  grid-area: title;
}

.Publications__letter {
  display: block;
  width: 2em;
  text-align: center;
  color: inherit;
}

.Publications__letter--active {
  font-weight: bold;
}

.Publications__grid {
  margin-left: 1px;
  grid-area: grid;
  border-collapse: collapse;
}

.Publications__grid tr:not(:last-child) {
  border-bottom: 1px solid #ebebeb;
}

.Publications__grid-head {
  font-weight: bold;
  font-family: 'HelveticaNeueW02-75Bold', Arial, Helvetica, sans-serif;
  color: #333;
  text-transform: uppercase;
  font-size: 11px;
}

.Publications__grid-head th {
  padding: 10px 0;
}

.Publications__name-header {
  text-align: left;
}

.Publications__grid td {
  padding: 10px 0;
  vertical-align: top;
}

td.Publications__year {
  text-align: center;
  vertical-align: top;
  font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
  font-size: 12px;
  font-weight: bold;
  color: #666;
  width: 160px;
}

.Publications__link {
  color: #096;
  font-size: 18px;
  font-family: 'Neo Sans W01', Arial, Helvetica, sans-serif;
  display: block;
}

.Publications__link::first-letter {
  text-transform: uppercase;
}

.Publications__details {
  display: flex;
  justify-content: space-between;
  font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
  font-size: 11px;
  margin: 5px 15px 0 0;
}

.Publications__files {
  color: #999;
}

.Publications__files-count {
  color: #333;
  font-family: 'Neo Sans W01', Arial, Helvetica, sans-serif;
}

.Publications__footer {
  margin-top: 50px;
  grid-area: footer;
}
</style>


<script>
import Pagination from './Pagination';

export default {
  components: {
    Pagination
  },
  computed: {
    page() {
      return this.$route.meta.data.page
    },
    totalPages() {
      return this.$route.meta.data.total_pages;
    },
    publications(){
      return this.$route.meta.data.publications;
    }
  }
}
</script>
