<template>
  <div class="Publication Subgrid">
    <h1 class="Publication__title">{{ publication.title }}</h1>

    <div class="Publication__content">
      <i>{{ publication.published ? 'Published' :'Not published' }}</i>
      <dl class="Publication__details">
        <div>
          <dt>Year:</dt>
          <dd>{{ publication.pub_year }}</dd>
        </div>
        <div>
          <dt>Authors:</dt>
          <dd>{{ publication.authors }}</dd>
        </div>
        <div>
          <dt>Journal:</dt>
          <dd>{{ publication.journal }}</dd>
        </div>
        <div>
          <dt>Files:</dt>
          <dd>
            <template v-for="(scan, ix) in publication.scans">
              <template v-if="ix > 0">,</template>
              <router-link :key="scan.id"
                          :to="{ name: 'scan-or-pub', params: { id: scan.url_slug || scan.id } }"
                          v-text="scan.scientific_name"
                          class="Publication__link" />
            </template>
          </dd>
        </div>
      </dl>

      <div class="Publication__abstract">
        {{ publication.abstract }}
      </div>

      <p><a v-if="publication.link" :href="publication.link">{{ publication.link }}</a></p>

      <b>Download:</b>
      <ul class="Publication__downloads">
        <li v-for="file in publication.files" :key="file.id">
          <a :href="file.file" :download="file.filename"><img src="/static/download.png" alt="" /> {{ file.name }}</a>
        </li>
      </ul>
    </div>

    <router-link class="Publication__back" :to="{ name: 'publications' }">Back</router-link>
  </div>
</template>

<script>
export default {
  computed:{
    publication(){
      return this.$route.meta.data;
    }
  }
}
</script>

<style>
.Publication {
  grid-column-start: 1;
  grid-column-end: 4;
  grid-template-areas: ". back title"
                       ". .    contents";
}

.Publication__title {
  grid-area: title;
  color: #096;
  font-family: 'Neo Sans W01', Arial, Helvetica, sans-serif;
  font-size: 24px;
  font-weight: normal;
  margin-bottom: 25px;
}

.Publication__content {
  grid-area: contents;
  font-size: 12px;
}

.Publication__back {
  grid-area: back;
  text-transform: uppercase;
  color: #333;
  font-size: 12px;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  padding: 16px;
}

.Publication__back::before {
  content: '« ';
}

.Publication__details {
  font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
  line-height: 20px;
  font-weight: bold;
}

.Publication__details dt {
  display: inline;
  color: #666;
}

.Publication__details dd {
  display: inline;
  margin-left: 0.25em;
}

.Publication__abstract {
  font-weight: bold;
  line-height: 20px;
}

.Publication__downloads {
  margin: 0;
  padding: 0;
}

.Publication__downloads li {
  list-style: none;
}

.Publication__link {
  color: #096;
}
</style>
