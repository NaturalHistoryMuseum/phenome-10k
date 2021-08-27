<template>
  <div class="Scan Content__subgrid">
    <img v-if="viewStill" :src="viewStill.file" />
    <CtmViewer v-else :src="ctm" />
    <div class="Content__sidebar">
      <router-link :to="{ name: 'library' }" class="Scan__back">« Back</router-link>
    </div>
    <h1>{{ title }}</h1>
    <p v-if="!scan.published">Not published</p>

    <div class="Scan__grid">
      <div class="Scan__column">
        <p>
          <template v-for="(tag, ix) in scan.tags">
            <router-link :key="tag.id"
                         :to="{ name: 'library', query: { [tag.category]: tag.taxonomy } }"
                         class="Scan__link">{{ tag.name }}
            </router-link><!--
         -->
            <template v-if="scan.tags[ix+1]">,</template>
          </template>
        </p>

        <dl class="Scan__datalist">
          <div>
            <dt>Alt Name:</dt>
            <dd>{{ scan.alt_name }}</dd>
          </div>
          <div>
            <dt>Location:</dt>
            <dd>{{ scan.specimen_location }}</dd>
          </div>
          <div>
            <dt>Specimen ID:</dt>
            <dd>{{ scan.specimen_id }}</dd>
          </div>
          <div>
            <dt>Additional Media:</dt>
            <dd>{{ scan.specimen_link }}</dd>
          </div>
        </dl>

        <div v-html="scan.description" />

        <div v-for="publication in scan.publications.filter(pub=>pub.published)" :key="publication.id">

          <div class="Scan__publication-details">
            <h2 class="Scan__related">Related Publication</h2>

            <dl class="Scan__datalist">
              <div>
                <dt>Title:</dt>
                <dd>
                  <router-link class="Scan__link" :to="{ name: 'publication', params: { id: publication.url_slug } }">
                    {{ publication.title }}
                  </router-link>
                </dd>
              </div>
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
            </dl>
          </div>

          <div class="Scan__pub-abstract" v-html="publication.abstract" />

          <p>
            Link:<br>
            <a class="Scan__link" :href="publication.link">{{ publication.link }}</a>
          </p>
        </div>
      </div>
      <div class="Scan__column-files">
        <h2 class="Scan__files-header">Files</h2>

        <Files title="Stills" :download="scan.url_slug + '/stills'">
          <div class="Scan__file" v-for="still in scan.stills" :key="still.id">
            <input type="image" :src="still.file + '?w=80'" @click="viewStill=still" :alt="still.name" />
            <div class="Scan__file-info">
              {{ still.name }}<br>
              {{ size(still.size) }}
            </div>
          </div>
        </Files>

        <Files title="3D / Web GL" :download="scan.source">
          <div class="Scan__file">
            <input v-if="scan.thumbnail" type="image" :src="scan.thumbnail + '?w=80'" @click="viewStill=null"
                   alt="Original file" />
            <div class="Scan__file-info">
              (Scan)
            </div>
          </div>
        </Files>

        <template v-for="publication in scan.publications.filter(pub => pub.published)">
          <Files v-for="file in publication.files" :key="file.id" title="PDF" :download="file.file">
            <div class="Scan__file-pdf">
              <a :href="file.file" class="Scan__file-pdf-text" :title="`Download PDF`" download>{{
                  publication.title
                                                                                                }}</a>
            </div>
            <div class="Scan__file-info">
              {{ file && file.name }}<br>
              {{ size(file.size) }}
            </div>
          </Files>
        </template>
      </div>
    </div>
  </div>
</template>

<style>
.Scan {
  padding: 60px 0 40px;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  font-size: 12px;
  line-height: 20px;
  display: contents;
}

.Scan__back {
  grid-column-start: 3;
  justify-self: start;
}

.Scan__grid {
  display: flex;
  justify-content: space-between;
}

.Scan__related {
  margin: 1em 0;
}

.Scan__related {
  margin: 0 0 10px;
  font-size: 12px;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  color: #096;
}

.Scan__datalist {
  margin: 0;

dt, dd {
  display: inline;
}

dd {
  margin-left: 0.5em;
}

dt {
  font-weight: bold;
}

}

.Scan__link {
  color: #999;
}

.Scan__publication-details {
  padding: 20px 0;
  margin: 20px 0;
  border-top: 1px solid #ebebeb;
  border-bottom: 1px solid #ebebeb;
}

.Scan__pub-abstract {
  font-size: 11px;
}

.Scan__column {
  flex: auto;
}

.Scan__column-files {
  flex-basis: 25%;
  margin-left: 10px;
}

.Scan__files-header {
  font-family: 'Supria Sans W01 Bold', Arial, Helvetica, sans-serif;
  font-size: 12px;
}

.Scan__file {
  display: flex;
  margin: 0.5px;
  align-items: center;
}

.Scan__file-pdf {
  font-size: smaller;
  height: 60px;
  width: 80px;
  background: linear-gradient(to bottom, #333, #666);
}

.Scan__file-pdf-text {
  background-image: linear-gradient(to bottom, #eee 50%, transparent);
  -webkit-text-fill-color: transparent;
  -webkit-background-clip: text;
  color: #666;
  background-clip: text;
  padding: 6px;
  display: block;
  width: 100%;
  height: 100%;
  line-height: normal;
  font-weight: bold;
  overflow: hidden;
}

.Scan__file-pdf-text:focus {
  outline-offset: -1px;
  outline: 1px dotted white;
}

.Scan__file-info {
  margin: 10px;
  min-width: 80px;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  font-size: 11px;
  line-height: initial;
  overflow: hidden;
}
</style>

<script>
import CtmViewer from '../CtmViewer';
import Files from './Files';

export default {
  components: {
    CtmViewer,
    Files
  },
  data() {
    return {
      viewStill: null
    };
  },
  computed: {
    scan() {
      return this.$route.meta.data;
    },
    title() {
      return this.scan.scientific_name ?
          this.scan.scientific_name[0].toUpperCase() + this.scan.scientific_name.substr(1) :
          'Unnamed Upload';
    },
    ctm() {
      return decodeURIComponent(this.scan.ctm);
    }
  },
  methods: {
    size(bytes) {
      return Math.floor(bytes / 1000) + 'k';
    }
  }
};
</script>
