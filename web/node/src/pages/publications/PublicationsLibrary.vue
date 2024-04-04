<template>
  <div :class="$style.main">
    <h1 class="Body__title">Publications</h1>
    <div class="Body__filters">
      <div :class="$style.filterControls">
        <Search :class="$style.search" name="q" v-model="q" />
        <div :class="$style.sort" v-if="routeData.showMine">
          Viewing:
          <ul :class="$style.sortList">
            <li :class="getMineLinkClass(false)">
              <router-link :to="getMineLink(false)">All</router-link>
            </li>
            <li :class="getMineLinkClass(true)">
              <router-link :to="getMineLink(true)">Mine</router-link>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <table :class="$style.table">
      <thead>
        <tr>
          <th>Year</th>
          <th>Name of Publication</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(pub, ix) in publications" :key="pub.id">
          <td>
            {{
              !publications[ix - 1] ||
              publications[ix - 1].pub_year !== pub.pub_year
                ? pub.pub_year
                : ''
            }}
          </td>
          <td>
            <router-link
              :class="$style.link"
              :to="{
                name: 'publications_view',
                params: { id: pub.url_slug || pub.id },
              }"
            >
              {{ pub.title }}
            </router-link>
            <div :class="$style.details">
              <div :class="$style.authors">
                {{ pub.authors }}
              </div>
              <div :class="$style.files">
                No. of Files:
                <span :class="$style.filesCount">{{ pub.scans.length }}</span>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <Pagination
      :page="page"
      :total="totalPages"
      :to="
        (page) => ({
          name: 'publications_library-paged',
          params: { page },
          query: this.$route.query,
        })
      "
      class="Body__pagination"
    />
  </div>
</template>

<script>
import Library from '../common/base/Library';

export default {
  name: 'PublicationsLibrary',
  extends: Library,
  components: {},
  data() {
    return {};
  },
  computed: {
    publications() {
      return this.routeData.publications;
    },
  },
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';
@import 'scss/vars';

@import '../common/styles/sort';
@import '../common/styles/table';

.main {
  display: contents;
}

.table {
  @include marginCol;
}

.details {
  display: flex;
  justify-content: space-between;
  font-size: $small-font-size;
  margin: 5px 15px 0 0;
}

.files {
  color: $palette-grey-2;
}

.filesCount {
  color: $palette-grey-1;
}

.search {
}
</style>
