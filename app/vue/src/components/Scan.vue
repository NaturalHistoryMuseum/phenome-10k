<template>
  <div class="Scan">
    <CtmViewer :src="scan.ctm" />
    <h1 class="Scan__title">{{ title }}</h1>
    <p v-if="!scan.published">Not published</p>

    <div class="Scan__grid">
      <div class="Scan__column">
        <p>
          <template v-for="(tag, ix) in scan.tags">
            <router-link :key="tag.id"
                        :to="{ name: 'library', query: { [tag.category]: tag.taxonomy } }"
                        class="Scan__link">{{ tag.name }}</router-link><!--
        ---><template v-if="scan.tags[ix+1]">, </template>
          </template>
        </p>

        <!--
          Location
          Specimen ID
          Description
          Related publication:
          Title
          Year
          Authors
          Journal
          Abstract
          Link
          Files:
          Stills
          3D/Web GL
          PDF
        -->
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
            <dt>Specimen URL:</dt>
            <dd>{{ scan.specimen_link }}</dd>
          </div>
        </dl>

        <p>
          {{ scan.description }}
        </p>


        <div v-for="publication in scan.publications" :key="publication.id">

          <div class="Scan__publication-details">
            <h2 class="Scan__related">Related Publication</h2>

            <dl class="Scan__datalist">
              <div>
                <dt>Title:</dt>
                <dd>{{ publication.title }}</dd>
              </div>
              <div>
                <dt>Year:</dt>
                <dd>{{ publication.year }}</dd>
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

          <p class="Scan__pub-abstract">
            {{ publication.abstract }}
          </p>

          <p>
            Link:<br>
            <a :href="publication.link">{{ publication.link }}</a>
          </p>
        </div>
      </div>
      <div class="Scan__column">
        <h2>Files</h2>

        <div class="Scan__files">
          <h3>Stills</h3>
          Download
          <div class="Scan__file" v-for="still in scan.stills" :key="still">
            <img :src="still">
            <div>
              Img name<br>
              Img size
            </div>
          </div>
        </div>
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

/* Todo: Combine title stuff with each other */
.Scan__title {
    color: #096;
    font-weight: 100;
    font-size: 36px;
    font-family: 'Neo Sans W01 Light', Helvetica, Arial, sans-serif;
    margin: 40px 0 30px;
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

.Scan__files {
  display: flex;
  flex-wrap: wrap;
}

.Scan__file {
  width: 100%;
  display: flex;
}
</style>

<script>
import CtmViewer from './CtmViewer';

export default {
  components: {
    CtmViewer
  },
  inject: ['defaultData'],
  computed: {
    scan() {
      return this.defaultData
    },
    title() {
      return this.scan.scientific_name[0].toUpperCase() + this.scan.scientific_name.substr(1)
    }
  }
}
</script>
