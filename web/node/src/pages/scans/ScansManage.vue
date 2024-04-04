<template>
  <div :class="$style.main">
    <h1 class="Body__title">Manage Uploads</h1>
    <div class="Body__filters">
      <Search v-model="q" name="q" />
    </div>
    <div :class="$style.sidebar">
      <router-link :class="getFilterClass()" :to="{ name: 'scans_manage' }"
        >All</router-link
      >
      <router-link
        :class="getFilterClass(f)"
        v-for="f of filterOptions"
        :to="{ name: 'scans_manage', query: { char: f } }"
        :key="f"
        >{{ f }}
      </router-link>
    </div>
    <table :class="$style.table">
      <thead>
        <tr>
          <th>Upload Date</th>
          <th>Name of Specimen</th>
          <th>Name of Uploader</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="scan in scans" :key="scan.id">
          <td>{{ getDateCreated(scan) }}</td>
          <td>
            <router-link
              :class="$style.link"
              :to="{
                name: 'scan_view',
                params: { id: scan.url_slug || scan.id },
              }"
            >
              {{ scan.scientific_name || '(unnamed specimen)' }}
            </router-link>
            <dl :class="$style.details">
              <template v-for="({ name, values }, ix) in getScanData(scan)">
                <template v-if="ix > 0">,</template>
                <dt :key="name">{{ name }}</dt>
                :
                <dd :key="name + '-val'">{{ values.join(', ') }}</dd>
              </template>
            </dl>
          </td>
          <td>
            {{ scan.author }}
          </td>
          <td>
            <form method="post" :class="$style.actions">
              <input
                name="csrf_token"
                type="hidden"
                :value="routeData.csrf_token"
              />
              <button
                :formaction="
                  $router.resolve({
                    name: 'scan_edit',
                    params: { id: scan.id },
                    query: { redirect: $route.fullPath },
                  }).href
                "
                :name="scan.published ? null : 'published'"
                value="On"
              >
                {{ scan.published ? 'Unpublish' : 'Publish' }}
              </button>
              <router-link :to="{ name: 'scan_edit', params: { id: scan.id } }"
                >Edit</router-link
              >
              <button name="delete" :value="scan.id" @click="confirmDelete">
                Delete
              </button>
            </form>
          </td>
        </tr>
      </tbody>
    </table>
    <Pagination
      :page="page"
      :total="totalPages"
      :to="
        (page) => ({
          name: 'scans_manage-paged',
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
import moment from 'moment';

export default {
  name: 'ScansManage',
  extends: Manage,
  data() {
    return {
      warningMsg:
        'This action will permenently delete the source file and all attachments.',
    };
  },
  computed: {
    scans() {
      return this.routeData.scans;
    },
    filterQ() {
      return this.$route.query.char;
    },
    filterOptions() {
      return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    },
  },
  methods: {
    /**
     * Generate human readable creation date for a scan
     */
    getDateCreated(scan) {
      const date = moment(scan.created);

      return date.format('YYYY.MM.DD');
    },
    /**
     * Generate an array of objects containing scan data item
     */
    getScanData(scan) {
      const data = [];
      if (scan.specimen_id) {
        data.push({
          name: 'Specimen ID',
          values: [scan.specimen_id],
        });
      }

      const elements = scan.tags.filter((tag) => tag.category === 'elements');
      if (elements.length > 0) {
        data.push({
          name: 'Elements',
          values: elements.map((el) => el.name),
        });
      }

      return data;
    },
  },
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';
@import 'scss/vars';

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

.title {
  grid-area: title;
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

  & > * {
    display: inline;
    margin: 0;
  }

  & dt {
    color: $palette-grey-2;
  }
}

.actions {
  display: flex;
  justify-content: flex-end;

  & > * {
    appearance: none;
    border: none;
    background: transparent;
    color: $palette-grey-1;
    cursor: pointer;
    padding: 0 5px;
    line-height: 1.2em;
    @include font-body;
    font-size: $small-font-size;

    &:hover {
      text-decoration: underline;
    }

    &:not(:last-child) {
      border-right: 1px solid $palette-grey-4;
    }
  }
}
</style>
