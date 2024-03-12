<template>
  <div :class="$style.main">
    <div :class="$style.title">
      <h1>{{ publication.title }}</h1>
      <span v-if="!publication.published" :class="$style.unpublished"
        >(Not published)</span
      >
    </div>

    <div :class="$style.sideLinks">
      <router-link :to="{ name: 'publications_library' }">« Back</router-link>
    </div>

    <div class="Body__content">
      <dl :class="$style.datalist">
        <dt>Year:</dt>
        <dd>{{ publication.pub_year }}</dd>
        <dt>Authors:</dt>
        <dd>{{ publication.authors }}</dd>
        <dt>Journal:</dt>
        <dd>{{ publication.journal }}</dd>
        <dt>Scans:</dt>
        <dd>
          <template v-for="(scan, ix) in publication.scans">
            <template v-if="ix > 0">,</template>
            <router-link
              :key="scan.id"
              :to="{
                name: 'scan_view',
                params: { id: scan.url_slug || scan.id },
              }"
              v-text="scan.scientific_name.trim()"
              :class="$style.link"
            />
          </template>
        </dd>
      </dl>

      <div :class="$style.abstract" v-html="publication.abstract" />

      <div>
        <a v-if="publication.link" :href="publication.link">{{
          publication.link
        }}</a>
      </div>

      <div :class="$style.downloads">
        <b v-if="publication.files.length > 0">Download:</b>
        <ul>
          <li v-for="file in publication.files" :key="file.id">
            <a :href="file.file" :download="file.filename"
              ><img src="/static/download.png" alt="" /> {{ file.name }}</a
            >
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import Page from '../common/base/Page';

export default {
  name: 'PublicationsView',
  extends: Page,
  computed: {
    publication() {
      return this.routeData;
    },
  },
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

@import '../common/styles/view';

.abstract {
  margin: 1em 0;
}

.downloads {
  margin: 1em 0;

  & > ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }
}
</style>
