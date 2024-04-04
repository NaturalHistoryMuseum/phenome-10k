<template>
  <div :class="$style.main">
    <h1 class="Body__title">Manage Publications</h1>
    <div class="Body__filters">
      <Search v-model="q" name="q" />
    </div>
    <div :class="$style.sidebar">
      <router-link
        :class="getFilterClass()"
        :to="{ name: 'publications_manage' }"
        >All</router-link
      >
      <router-link
        :class="getFilterClass(f)"
        v-for="f of filterOptions"
        :to="{ name: 'publications_manage', query: { pub_year: f } }"
        :key="f"
        >{{ f }}
      </router-link>
    </div>
    <table :class="$style.table">
      <thead>
        <tr>
          <th>Year</th>
          <th>Name of Publication</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="publication in publications" :key="publication.id">
          <td>{{ publication.pub_year }}</td>
          <td>
            <router-link
              :class="$style.link"
              :to="{
                name: 'publications_view',
                params: { id: publication.url_slug || publication.id },
              }"
            >
              {{ publication.title }}
            </router-link>
            <div :class="$style.details">{{ publication.authors }}</div>
          </td>
          <td :class="$style.actionsCol">
            <form method="post" :class="$style.actions">
              <input type="hidden" name="id" :value="publication.id" />
              <button
                name="action"
                :value="publication.published ? 'unpublish' : 'publish'"
              >
                {{ publication.published ? 'Unpublish' : 'Publish' }}
              </button>
              <router-link
                :to="{
                  name: 'publications_edit',
                  params: { id: publication.id },
                }"
                >Edit</router-link
              >
              <button name="action" value="delete" @click="confirmDelete">
                Delete
              </button>
            </form>
            <div :class="$style.files">
              No. of Files:
              <span :class="$style.filesCount">{{
                publication.scans.length
              }}</span>
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
          name: 'publications_manage-paged',
          params: { page },
          query: this.$route.query,
        })
      "
      class="Body__pagination"
    />
  </div>
</template>

<script>
import Manage from '../common/base/Manage';

export default {
  extends: Manage,
  data() {
    return {
      warningMsg:
        'This action will permenently delete the record and all attachments.',
    };
  },
  computed: {
    publications() {
      return this.routeData.publications;
    },
    filterQ() {
      return this.$route.query.pub_year;
    },
    filterOptions() {
      return this.routeData.years;
    },
  },
  methods: {},
};
</script>

<style module lang="scss">
@import '../common/styles/table';

.main {
  display: contents;
}

.table {
  @include marginCol;
  @include stripes;

  & td {
    vertical-align: middle;
  }
}

.sidebar {
  grid-column: side1;
  grid-row: content-start;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-self: end;
  width: max-content;
  padding: 0 2px;
  margin: 4.5px 10px 0;
  text-transform: uppercase;
  font-size: $small-font-size;
  color: $palette-grey-2;
  line-height: 1.5em;
}

.sideFilter {
  text-align: center;
  color: inherit;

  &--active {
    font-weight: bold;
    font-style: italic;
  }
}

.details {
  font-size: $small-font-size;
  margin: 5px 0 0;
  color: $palette-grey-2;
}

.actionsCol {
  font-size: $small-font-size;
  text-align: right;
}

.actions {
  display: flex;
  justify-content: flex-end;

  & > * {
    font-size: $small-font-size;
    appearance: none;
    border: none;
    background: transparent;
    color: $palette-grey-1;
    cursor: pointer;
    padding: 0 5px;
    line-height: 1.2em;
    @include font-body;

    &:hover {
      text-decoration: underline;
    }

    &:not(:last-child) {
      border-right: 1px solid $palette-grey-4;
    }

    &:first-child {
      padding-left: 0;
    }
  }
}

.files {
  color: $palette-grey-2;
  padding: 0 5px;
}

.filesCount {
  color: $palette-grey-1;
}
</style>
