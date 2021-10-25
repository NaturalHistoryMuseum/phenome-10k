<template>
  <div :class="$style.main">
    <div :class="$style.title">
      <h1>{{ title }}</h1>
      <span v-if="!scan.published" :class="$style.unpublished">(Not published)</span>
    </div>

    <div :class="$style.sideLinks">
      <router-link :to="{ name: 'scans_library' }">« Back</router-link>
    </div>

    <div class="Body__content">
      <div :class="$style.viewer">
        <img v-if="viewStill" :src="viewStill.file" />
        <CtmViewer v-else :src="ctm" />
      </div>

      <div :class="$style.details">
        <div>
          <div :class="$style.tags">
            <template v-for="(tag, ix) in scan.tags">
              <router-link :key="tag.id"
                           :to="{ name: 'scans_library', query: { [tag.category]: tag.taxonomy } }"
                           :class="$style.tag">{{ tag.name }}<!--
          --></router-link>
            </template>
          </div>

          <dl :class="$style.datalist">
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
              <dd>{{ scan.specimen_link || '-' }}</dd>
            </div>
          </dl>

          <div :class="$style.scanDesc" v-html="scan.description" />

          <div :class="$style.links">
            <a :href="`https://gbif.org/occurrence/${scan.gbif_occurrence_id}`" v-if="scan.gbif_occurrence_id"
               target="_blank">View specimen {{ scan.specimen_id }} on GBIF</a>
            <a :href="`https://gbif.org/species/${scan.gbif_species_id}`" v-if="scan.gbif_species_id" target="_blank">View
              <i>{{ scan.scientific_name }}</i> on GBIF</a>
            <a :href="nhmPortalLink" v-if="nhmPortalLink" target="_blank">View specimen {{ scan.specimen_id }} on the Natural History
                                                          Museum Data Portal</a>
          </div>

          <div v-for="publication in scan.publications.filter(pub=>pub.published)" :key="publication.id"
               :class="$style.publicationDetails">

            <h2>Related Publication</h2>

            <dl :class="$style.datalist">
              <div>
                <dt>Title:</dt>
                <dd>
                  <router-link :to="{ name: 'publications_view', params: { id: publication.url_slug } }">
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

            <div :class="$style.pubAbstract" v-html="publication.abstract" />

            <div :class="$style.pubLink" v-if="publication.link">
              <b>Link:</b>
              <a :href="publication.link">{{ publication.link }}</a>
            </div>
          </div>
        </div>
        <div>
          <h2>Files</h2>

          <Files title="Stills" :download="'/files/stills/' + scan.url_slug">
            <div :class="$style.file" v-for="still in scan.stills" :key="still.id">
              <div :class="$style.filePreview">
                <input type="image" :src="still.file + '?w=80'" @click="viewStill=still" :alt="still.name" />
              </div>
              <div :class="$style.fileInfo">
                {{ still.name }}<br>
                {{ size(still.size) }}
              </div>
            </div>
          </Files>

          <Files title="3D / Web GL" :download="scan.source">
            <div :class="$style.file">
              <div :class="$style.filePreview">
                <input v-if="scan.thumbnail" type="image" :src="scan.thumbnail + '?w=80'" @click="viewStill=null"
                       alt="Original file" />
              </div>
              <div :class="$style.fileInfo">
                (Scan)
              </div>
            </div>
          </Files>

          <template v-for="publication in scan.publications.filter(pub => pub.published)">
            <Files v-for="file in publication.files" :key="file.id" title="PDF" :download="file.file">
              <div :class="$style.file">
                <div :class="$style.filePreview">
                  <a :href="file.file" :title="`Download PDF`" download>
                    {{ publication.title }}
                  </a>
                </div>
                <div :class="$style.fileInfo">
                  {{ file && file.name }}<br>
                  {{ size(file.size) }}
                </div>
              </div>
            </Files>
          </template>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import CtmViewer from './components/CtmViewer';
import Files from './components/Files';
import Page from '../common/base/Page';

export default {
  extends: Page,
  components: {
    CtmViewer,
    Files
  },
  data() {
    return {
      viewStill: null,
      nhmPortalLink: null
    };
  },
  computed: {
    scan() {
      return this.routeData;
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
    },
    async getNHMPortalLink() {
      let searchBody = {
        gbifID: this.scan.gbif_occurrence_id
      };
      const res = await fetch('https://data.nhm.ac.uk/api/3/action/datastore_search?resource_id=05ff2255-c38a-40c9-b657-4ccb55ab2feb&filters=' + JSON.stringify(searchBody));
      if (!res.ok) {
        console.log(res);
        return;
      }
      const results = await res.json();
      let record = results.result.records[0];
      if (record) {
        this.nhmPortalLink = `https://data.nhm.ac.uk/object/${ record.occurrenceID }`;
      }
      else {
        this.nhmPortalLink = null;
      }
    }
  },
  mounted() {
    if (this.scan.gbif_occurrence_id) {
      this.getNHMPortalLink();
    }
  }
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

@import '../common/styles/view';

.viewer {
  img {
    max-width: 100%;
  }
}

.details {
  display: grid;
  grid-gap: 40px;
  grid-template-columns: 1fr 25%;
}

.tags {
  margin: 1em 0;

  & .tag {
    color: $palette-grey-2;

    &:not(:last-child)::after {
      content: ', ';
      color: $palette-grey-5;
    }
  }
}

.datalist {
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

.links {
  display: grid;
  margin-top: 1em;
  font-size: $small-font-size;
}

.scanDesc {
  margin-top: 1em;

  &::first-letter {
    text-transform: capitalize;
  }
}

.publicationDetails {
  padding: 20px 0;
  margin: 20px 0;
  border-top: 1px solid $palette-grey-5;

  & .pubAbstract {
    margin: 1em 0;
  }

  & .pubLink {
    display: grid;
  }

  & h2 {
    margin-top: 0;
  }
}


.file {
  display: grid;
  grid-template-columns: 80px 1fr;
  grid-gap: 10px;
  font-size: $small-font-size;
  line-height: 1.2em;
  margin-bottom: 1em;

  & > .filePreview {
    @include viewerGradient;
    color: white;
    word-break: break-all;
    height: 60px;
    overflow: hidden;

    & > * {
      padding: 5px;
      background-image: linear-gradient(to bottom, white 50%, transparent);
      -webkit-text-fill-color: transparent;
      -webkit-background-clip: text;
      background-clip: text;
      color: white;
      display: block;
      width: 100%;
      height: 100%;
      font-size: $small-font-size;
      @include font-body;

      &:focus {
        outline-offset: -1px;
        outline: 1px dotted white;
      }
    }
  }
}

.fileInfo {
  margin: 10px;
  min-width: 80px;
  font-size: $small-font-size;
  line-height: initial;
  overflow: hidden;
}
</style>


