<template>
  <div :class="$style.main">
    <div :class="$style.title">
      <h1>{{ $route.name === 'scan_edit' && scan ? 'Editing ' + scan.scientific_name : 'Upload New' }}</h1>
    </div>

    <div :class="['Body__content', $style.sectionGrid]">

      <div :class="$style.section" :id="$style.upload">
        <form :action="formAction" method="post" enctype="multipart/form-data">
          <input type="hidden" name="csrf_token" :value="csrf">
          <Errors v-if="error" :errors="[error]" />
          <Errors v-if="errors" :errors="errors" />
          <div :class="$style.sectionHead">
            <h2 :class="$style.sectionTitle">Browse and preview STL file</h2>
          </div>
          <CtmViewer v-if="scan && scan.ctm" ref="canvas" :src="scan.ctm" height=400px width=500px />
          <Upload3D v-else @change="upload" :progress="progress"
                    :status="status || (scan && scan.source && 'Uploaded' )"
                    :errors="form.file.errors"></Upload3D>
        </form>
      </div>

      <div :class="$style.section" :id="$style.stills">
        <div :class="$style.sectionHead">
          <h2 :class="$style.sectionTitle">Take Stills</h2>
          <span :class="$style.sectionSubTitle">Move image into appropriate position and click the button below (Minimum of 1 snapshot image, maximum of 6 images).</span>
        </div>
        <div :class="$style.stillCaptureName">
          <label>Label: <input v-model="stillName"></label>
          <Button type="button" @click="captureStill">Capture</Button>
        </div>
        <Errors :errors="form.stills.errors" />

        <div :class="$style.stillsGrid">
          <div v-for="{ name, file, id } in stills" :key="file">
            <Delete type="button" @click="removeStill(id)">Remove Image</Delete>
            <img :src="file" :class="$style.stillImage" />
            <div :class="$style.stillName">{{ name }}</div>
          </div>
        </div>
      </div>

      <form :id="$style.details" :action="formAction" method="post" @submit.prevent="submit" novalidate>
        <input type="hidden" name="csrf_token" :value="csrf">
        <div :class="$style.col1">
          <div :class="$style.section" :id="$style.scientificName">
            <TextInput name="scientific_name" :data="form.scientific_name" @keyup="e => searchGbif(e.target.value)"
                       autocomplete="off" type="text">
              <div :class="$style.sectionHead">
                <h2 :class="$style.sectionTitle">Scientific Name</h2>
              </div>
            </TextInput>
            <div v-if="gbifSelectedId" :class="$style.gbifSelectedEntry">
              <span>
                <i>{{ gbifSelectedEntry.name }}</i> {{ gbifSelectedEntry.details }}
              </span>
              <span @click="deselectGbifSpecies">x</span>
            </div>
            <div v-else-if="gbifData.length < 1" :class="$style.gbifSelected">No associated GBIF record</div>
            <div v-else-if="gbifData.length < 2" :class="$style.gbifSelected">
              <input type="hidden" name="gbif_species_id" :value="gbifData[0].id">
              <i>{{ gbifData[0].name }}</i> {{ gbifData[0].details }}
            </div>
            <ul v-else :class="$style.gbifList">
              <li v-for="entry in gbifData" :key="entry.id">
                <label>
                  <input type="radio" name="gbif_species_id" :value="entry.id" v-model="gbifSelectedId"
                         @click="selectGbifSpecies(entry)">
                  <i>{{ entry.name }}</i> {{ entry.details }}
                </label>
              </li>
            </ul>
          </div>

          <div :class="$style.section" :id="$style.specimen">
            <fieldset>
              <legend :class="$style.sectionHead">
                <h2 :class="$style.sectionTitle">Specimen</h2>
                <span :class="$style.sectionSubTitle">Please enter relevant specimen information</span>
              </legend>
              <TextInput :class="$style.formLabel" name="alt_name" :data="form.alt_name" type="text">
                Alt. Name
              </TextInput>
              <TextInput :class="$style.formLabel" name="specimen_location" :data="form.specimen_location" type="text">
                Specimen Location
              </TextInput>
              <TextInput :class="$style.formLabel" name="specimen_id" :data="form.specimen_id" type="text">
                Specimen ID
              </TextInput>
              <TextInput :class="$style.formLabel" name="specimen_url" :data="form.specimen_url" type="text">
                Additional Media
              </TextInput>
            </fieldset>
          </div>

          <div :class="$style.section" :id="$style.description">
            <TextInput type="textarea" name="description" :data="form.description">
              <div :class="$style.sectionHead">
                <h2 :class="$style.sectionTitle">Description</h2>
              </div>
            </TextInput>
          </div>

          <div :class="$style.section" :id="$style.publications">
            <fieldset>
              <legend :class="$style.sectionHead">
                <h2 :class="$style.sectionTitle">Publications</h2>
                <span :class="$style.sectionSubTitle">Assign any relevant publications to the scan.</span>
              </legend>
              <div :class="$style.tabs">
                <button type="button" @click="myPubs=true" :class="pubsTabClass(myPubs)">My Pubs</button>
                <button type="button" @click="myPubs=false" :class="pubsTabClass(!myPubs)">All Pubs</button>
              </div>
              <div :class="$style.tabsContent">
                <div>
                  <div :class="$style.listSearch">
                    <input type="text" name="pub_query" @keyup="pubSearch"
                           :placeholder="myPubs ? 'Search My Publications' : 'Search Publications'"
                           autocomplete="off" :title="myPubs ? 'Search your own publication titles' : 'Search all publication titles'"/>
                  </div>
                  <ul :class="$style.listbox">
                    <li v-for="pub in pubSearchResults" :key="pub.id">
                      <input :class="$style.checkbox" type="checkbox" :value="pub.id" :id="'pub' + pub.id"
                             v-model="selectedPubIds">
                      <label :for="'pub' + pub.id">{{ pub.title }}</label>
                    </li>
                  </ul>
                </div>
                <ul :class="$style.listbox">
                  <li v-for="{id, title} in selectedPubs" :key="id">
                    <input :class="$style.checkbox" name="publications" type="checkbox" :value="id" :id="'sel-pub' + id"
                           v-model="selectedPubIds">
                    <label :for="'sel-pub' + id">{{ title }}</label>
                  </li>
                </ul>
              </div>
              <Errors :errors="form.publications.errors" />
            </fieldset>
          </div>
        </div>

        <div :class="$style.col2">
          <div :class="$style.section" :id="$style.categories">
            <div :class="$style.sectionHead">
              <h2 :class="$style.sectionTitle">Categories</h2>
              <span :class="$style.sectionSubTitle">
              Assign the relevant tags to this entry.
              At least one category in each of Geologic Age, Elements and Ontogenetic Age is required.
            </span>
            </div>
            <fieldset>
              <legend :class="$style.field">Geologic Age</legend>
              <div :class="$style.listbox">
                <Tree :items="form.geologic_age.choices" #node="option" childKey="children" :class="$style.tree">
                  <li>
                    <input type="checkbox" :class="$style.checkbox" name="geologic_age" :value="option.id"
                           :id="'geo-age' + option.id"
                           :checked="(form.geologic_age.data || [] ).some(tag => option.id===tag.id)">
                    <label :for="'geo-age' + option.id">{{ option.name }}</label>
                    <component :is="option.children" />
                  </li>
                </Tree>
              </div>
              <Errors :errors="form.geologic_age.errors" />
            </fieldset>
            <fieldset>
              <legend :class="$style.field">Ontogenetic Age</legend>
              <ul :class="$style.listbox">
                <li v-for="option in form.ontogenic_age.choices" :key="option.id">
                  <input type="checkbox" :class="$style.checkbox" name="ontogenic_age" :value="option.id"
                         :id="'onto-age' + option.id"
                         :checked="(form.ontogenic_age.data || [] ).some(tag => option.id===tag.id)">
                  <label :for="'onto-age' + option.id">{{ option.name }}</label>
                </li>
              </ul>
              <Errors :errors="form.ontogenic_age.errors" />
            </fieldset>
            <fieldset>
              <legend :class="$style.field">Elements</legend>
              <div :class="$style.listbox">
                <Tree :items="form.elements.choices" #node="option" childKey="children" :class="$style.tree">
                  <li>
                    <input type="checkbox" :class="$style.checkbox" name="elements" :value="option.id"
                           :id="'elements' + option.id"
                           :checked="(form.elements.data || [] ).some(tag => option.id===tag.id)">
                    <label :for="'elements' + option.id">{{ option.name }}</label>
                    <component :is="option.children" />
                  </li>
                </Tree>
              </div>
              <Errors :errors="form.elements.errors" />
            </fieldset>
          </div>

        </div>
        <div :id="$style.footer">
          <div>
            <input type="checkbox" :class="$style.checkbox" name="published" :checked="form.published.data" id="submit">
            <label for="submit">Publish</label>
          </div>
          <Button big>Save</Button>
        </div>
      </form>
    </div>

  </div>
</template>

<script>
import Tree from './components/tree.js';
import CtmViewer from './components/CtmViewer';
import Upload3D from './components/Upload3D';
import { Button, Delete, Errors, TextInput } from '../common/forms';

async function jsonOrText(source) {
  try {
    return source.json ? await source.json() : JSON.parse(source);
  } catch (e) {
    if (e instanceof SyntaxError) {
      console.warn(e);
      return source.text ? await source.text() : source;
    }

    throw e;
  }
}

function* blobIterator(blob, chunkSize = 500000) {
  for (let i = 0; i < blob.size; i += chunkSize) {
    yield [
      blob.slice(i, i + chunkSize),
      100 * i / blob.size
    ];
  }
}

const xhrUpload = async (form, progress) => {
  const formData = new FormData(form);

  const file = formData.get('file');
  const uploadRequest = await fetch('/files/', { method: 'POST' });
  if (!uploadRequest.ok) {
    throw new Error('POST to /files/ failed');
  }
  const uploadEndpoint = uploadRequest.headers.get('Location');

  for (const [blob, pc] of blobIterator(file)) {
    const res = await fetch(uploadEndpoint, { method: 'PATCH', body: blob });
    if (!res.ok) {
      throw new Error('Patch failed');
    }
    progress(Math.round(pc));
  }

  const uploadId = uploadEndpoint.split('/').pop();

  formData.set('file', uploadId + '/' + file.name);

  const xhr = new XMLHttpRequest();
  xhr.open('POST', form.action + '?noredirect=1');
  xhr.setRequestHeader('Accept', 'application/json');
  const ready = new Promise((res, rej) => {
    xhr.onload = async () => {

      if (xhr.status >= 400) {
        const responseData = await jsonOrText(xhr.responseText);
        rej(responseData);
        return;
      }

      res(xhr);
    };
    xhr.onerror = (progressEvent) => rej('The upload failed due to a network issue.');
  });

  xhr.upload.onprogress = function (event) {
    if (event.lengthComputable) {
      progress(Math.round((event.loaded / event.total) * 100));
    }
  };

  xhr.send(formData);

  return ready;
};

export default {
  name: 'ScansEdit',
  props: [
    'error',
  ],
  data() {
    const data = this.$route.meta.data;
    const pubSearchResults = data.form.publications.choices;
    const allPubs = data.scan ? pubSearchResults.concat(data.scan.publications) : pubSearchResults;
    const publications = allPubs.reduce((o, pub) => Object.assign(o, { [pub.id]: pub }), {});
    const gbifData = (data.scan && data.scan.gbif_species_id) ? [{
      id: data.scan.gbif_species_id,
      name: data.scan.scientific_name,
      details: ''
    }] : [];
    const gbifSelectedId = data.scan && data.scan.gbif_species_id;

    return {
      progress: null,         // Upload progress of the model file
      status: null,           // Upload status of the model file
      processing: false,      // Whether or not the upload is being processed
      gbifData,               // List of GBIF search results
      gbifSelectedId,         // Selected GBIF result
      gbifSelectedEntry: {},  // Selected GBIF result details (for display)
      stillName: '',          // Contents of the Still Name text input
      myPubs: true,           // Search only for publications created by current user
      pubSearchResults,       // List of results for publication search
      publications,           // Object containing all publications, keyed by ID
      selectedPubIds: (data.form.publications.data || []).map(pub => pub.id), // Array of selected publication IDs
      form: data.form,
      scan: data.scan,
      csrf: data.csrf_token,
      errors: []
    };
  },
  mounted() {
    if (this.scan) {
      this.searchGbif(this.scan.scientific_name);

      if (this.scan.source && !this.scan.ctm) {
        this.processUpload();
      }
    }
  },
  watch: {
    '$route.meta'(meta) {
      this.form = meta.data.form;
      this.scan = meta.data.scan;
    },
    /* When we switch the publications tab, empty the list of search results until the user types */
    myPubs() {
      this.pubSearchResults = [];
    }
  },
  computed: {
    /**
     * List of selected pub
     */
    selectedPubs() {
      return this.selectedPubIds.map(id => this.publications[id]);
    },
    stills() {
      return this.scan ? this.scan.stills : [];
    },
    formAction() {
      return this.scan ? this.$router.resolve({ name: 'scan_edit', params: this.scan }).href : '';
    }
  },
  methods: {
    logme() {
      console.log(this.scan);
    },
    async searchGbif(term) {
      if ((!term) || this.gbifSelectedId) {
        this.gbifData = [];
        return;
      }

      term = encodeURIComponent(term);
      const res = await fetch(`//api.gbif.org/v1/species/suggest?q=${ term }&datasetKey=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c&rank=SPECIES`);
      const results = await res.json();
      this.gbifData = results.map(
          entry => ({
            id: entry.key,
            name: entry.canonicalName,
            details: `${ entry.scientificName.replace(entry.canonicalName, '') } (${ entry.kingdom })`
          })
      );
    },
    /**
     * Automatically fill out the name field when user selects a GBIF item
     */
    selectGbifSpecies(species) {
      this.form.scientific_name.data = species.name;
      this.gbifSelectedEntry = species;
    },
    deselectGbifSpecies() {
      this.form.scientific_name.data = null;
      this.gbifSelectedId = null;
      this.gbifSelectedEntry = null;
      this.gbifData = [];
    },
    async submit({ target }) {
      const data = new FormData(target);
      const res = await fetch(target.action, {
        method: 'POST',
        headers: { accept: 'application/json' },
        body: data
      });

      if (res.status >= 400) {
        const reponseData = await jsonOrText(res);
        this.errors = Array.isArray(responseData) ? responseData : [responseData];
      }

      const json = await res.json();
      this.form = json.form;

      const url = res.url.replace(new URL(res.url).origin, '');
      this.$router.push(url);

      this.$nextTick(
          () => {
            const err = document.querySelector('.Errors:not(:empty)');
            if (err) {
              err.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
            } else {
              window.scrollTo(0, 0);
            }
          }
      );
    },
    /**
     * Delete a still by its attachment id
     */
    async removeStill(id) {
      const res = await fetch(`/files/stills/${ id }`, {
        method: 'DELETE',
        headers: { accept: 'application/json' }
      });
      const json = await res.json();
      if (json.scan) {
        this.scan = json.scan;
      }
    },
    async captureStill() {
      this.form.stills.errors = [];

      if (!this.stillName) {
        this.form.stills.errors = ['Please enter a name for the captured image'];
        return;
      }

      // I don't know why the limit is six, it just is
      if (this.stills.length >= 6) {
        this.form.stills.errors = ['There are too many stills, please remove a still.'];
        return;
      }

      // Use the label as the filename and have the server convert it to a secure filename
      const still = await this.$refs.canvas.captureStill(this.stillName);

      const data = new FormData();
      data.append('csrf_token', this.csrf);
      data.append('attachments', still, this.stillName);
      const res = await fetch(this.formAction, {
        method: 'POST',
        headers: { 'accept': 'application/json' },
        body: data
      });

      const json = await res.json();
      this.scan = json;
      this.stillName = '';
    },
    async upload(form) {
      try {
        const { responseText, responseURL } = await xhrUpload(form, p => {
          this.progress = p;
          if (p === 100) {
            this.status = 'Compressing...';
          }
        });
        const { scan: { id } } = JSON.parse(responseText);
        const res = await this.processUpload(id);
        const scan = await res.json();
        if (scan) {
          this.scan = scan;
        } else {
          this.$router.push(responseURL);
        }
      } catch (e) {
        this.progress = null;
        this.form.file.errors = [e];
      }
    },
    async processUpload(id = this.scan.id) {
      this.processing = true;
      this.progress = 100;
      this.status = 'Creating CTM file...';

      while (!this.scan || !this.scan.ctm) {
        await new Promise(resolve => setTimeout(resolve, 3000));

        const result = await fetch('/' + id, {
          headers: {
            Accept: 'application/json'
          }
        });

        if (result.status >= 400) {
          this.progress = null;
          this.status = null;
          this.form.file.errors = [await result.text()];
        } else {
          const scan = await result.json();
          if (scan) {
            this.scan = scan;
          }
        }
      }

      this.processing = false;

      return result;
    },
    async pubSearch(event) {
      const query = encodeURIComponent(event.target.value);
      const mine = this.myPubs ? '&mine' : '';
      const res = await fetch(`/publications?title=${ query }${ mine }`, { headers: { accept: 'application/json' } });
      this.pubSearchResults = (await res.json()).publications;
      // Add to the big list of all publications in case we want to reference it later
      for (const pub of this.pubSearchResults) {
        if (!(pub.id in this.publications)) {
          this.$set(this.publications, pub.id, pub);
        }
      }
    },
    /**
     * Return the class names for the publication search tabs
     * @param active {bool} True if the tab is currently active
     */
    pubsTabClass(active) {
      let cssClasses = {};
      cssClasses[this.$style.tab] = true;
      cssClasses[this.$style['tab--active']] = active;
      return cssClasses;
    }
  },
  components: {
    TextInput,
    Errors,
    Upload3D,
    CtmViewer,
    Tree,
    Button,
    Delete
  }
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';
@import '../common/styles/edit';

.sectionGrid {
  grid-template-areas: 'upload upload'
                       'stills stills'
                       'col1   col2  '
                       'footer footer';
  grid-template-columns: 2fr 1fr;
}

#details {
  display: contents;

  & .col1 {
    grid-area: col1;
    display: flex;
    flex-direction: column;

    & > .section {
      margin-top: $gaps / 2;

      &:last-of-type {
        flex-grow: 1;
      }
    }
  }

  & .col2 {
    grid-area: col2;
  }

  & .section:last-of-type {
    border-bottom: none;
  }
}

#upload {
  grid-area: upload;
}

#stills {
  grid-area: stills;

  & .stillCaptureName {
    display: flex;
    height: 2em;

    input {
      border: 1px solid $palette-grey-4;
      border-right: none;
      padding: 3px 10px;
      margin-left: 10px;
      width: 200px;
      height: 100%;
      @include font-body;
      font-size: $small-font-size;
    }

    button {
      display: inline-block;
      min-width: 50px;
      padding: 0 20px;
    }
  }

  & .stillsGrid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    padding: 20px 0;
    grid-gap: 20px;

    & > * {
      display: grid;
    }

    & .stillImage {
      max-width: 100%;
    }

    & .stillName {
      color: $palette-grey-3;
      margin-top: 5px;
      font-size: $small-font-size;
      justify-self: center;
    }
  }
}

#scientificName {
  .gbifSelected {
    font-size: $small-font-size;
    color: $palette-grey-3;
    margin: 5px 0 15px;
  }

  .gbifSelectedEntry {
    display: flex;
    font-size: $small-font-size;
    margin: 5px 0 15px;

    & > *:first-child {
      flex-grow: 1;
      color: $palette-grey-3;
    }

    & > *:last-child {
      color: $palette-primary;
      font-weight: bold;
      cursor: pointer;
    }
  }

  .gbifList {
    list-style: none;
    padding: 5px 0 15px;
    margin: 0;
    font-size: $small-font-size;

    & input {
      margin: 0 5px 0 0;
      vertical-align: middle;
    }

    & label {
      padding: 5px;
      display: block

      &:hover {
        background: $palette-grey-7;
        cursor: pointer;
      }
    }
  }
}

#specimen {

}

#description {
  & textarea {
    resize: vertical;
  }
}

#publications {
  & > fieldset {
    height: 100%;
  }

  .tabs {
    border-bottom: 1px solid $palette-grey-3;
    text-align: center;
  }

  .tab {
    cursor: pointer;
    font-weight: bold;
    background: none;
    margin-bottom: -1px;
    margin-left: 10px;
    font-size: 14px;
    border: 1px solid $palette-grey-3;
    padding: 7px 65px;
    display: inline-block;
    text-transform: uppercase;
    color: $palette-grey-3;

    &--active {
      border-bottom: 1px solid #fff;
      color: $palette-primary;
    }
  }

  .tabsContent {
    padding: 20px 15px;
    display: flex;
    margin: -7.5px;
    height: 100%;

    & > * {
      flex-basis: 50%;
      margin: 7.5px;
      border: 1px solid $palette-grey-3;
    }
  }

  .listSearch {
    width: 100%;
    display: flex;

    & input {
      border: 0;
      flex-grow: 1;
      padding: 5px;
      @include font-body;
      font-size: $small-font-size;
      color: $palette-grey-3;
      border-bottom: 1px solid $palette-grey-3;
    }
  }

  .checkbox + label {
    margin-bottom: 1em;
  }
}

#categories {
  .listbox {
    border: 1px solid $palette-grey-3;
  }

  .checkbox + label {
    margin-bottom: 5px;
  }

  .tree {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .tree .tree {
    padding-left: 15px;
  }
}

#footer {
  grid-area: footer;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;

  & > * {
    margin: 10px 50px;
  }
}

.formLabel {
  display: block;
  margin: 15px 0 5px;
}

fieldset {
  border: none;
  padding: 0;
  margin: 0;
}

.listbox {
  min-height: 100px;
  padding: 10px;
  list-style: none;
  margin: 0;
  color: $palette-grey-3;
  font-size: $small-font-size;
}

.checkbox {
  display: none;

  & + label {
    cursor: pointer;
    display: block;
    padding: 0 0 0 15px;
    line-height: 1.4em;
    position: relative;

    &::before {
      background: url('/static/tick-box.png') no-repeat;
      background-size: contain;
      content: '';
      height: 9px;
      width: 9px;
      position: absolute;
      left: 0;
      top: 0.4em;
    }
  }

  &:checked + label::before {
    background-image: url('/static/tick-box-selected.png');
  }

  &:focus + label {
    outline: 1px dotted;
  }
}


</style>
