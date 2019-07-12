<template>
  <div class="Upload Subgrid">
    <h1 class="Upload__title">{{ scan ? "Edit: " + scan.scientific_name : "Upload New" }}</h1>
    <form class="Upload__upload" :action="formAction" method="post" enctype="multipart/form-data">
      <input type="hidden" name="csrf_token" :value="csrf">
      <Errors v-if="error" :errors="[error]" />
      <h2 class="Upload__section-title Upload__section-head">Browse and preview STL file</h2>
      <CtmViewer v-if="scan && scan.ctm" ref="canvas" :src="scan.ctm" height=400px width=500px />
      <Upload3D v-else @change="upload" :progress="progress" :errors="form.file.errors"></Upload3D>
    </form>
    <div class="Upload__stills">
      <span class="Upload__section-title Upload__section-head">Take Stills</span> - Move image into appropriate position and click the button below (Minimum of 1 snapshot image, maximum of 6 images).

      <div class="Upload__still-capture-name">
        <label>Label: <input class="TextInput__input" v-model="stillName"></label>
        <Button type="button" @click="captureStill">Capture</Button>
      </div>
      <Errors :errors="form.stills.errors" />

      <div v-for="{ name, file, id } in stills" :key="file" class="Upload__still">
        <Delete type="button" @click="removeStill(id)">Remove Image</Delete>
        <img :src="file" class="Upload__still-image" />
        <div class="Upload__still-name">{{ name }}</div>
      </div>
    </div>
    <form class="Upload__details" :action="formAction" method="post" @submit.prevent="submit" novalidate>
      <input type="hidden" name="csrf_token" :value="csrf">
      <div class="Upload__column">
        <TextInput name="scientific_name" :data="form.scientific_name" @keyup="e => searchGbif(e.target.value)" autocomplete="off">
          <h2 class="Upload__section-title Upload__section-head">Scientific Name</h2>
        </TextInput>
        <div v-if="gbifData.length < 1" class="Upload__gbif-selected">No associated GBIF record</div>
        <div v-else-if="gbifData.length < 2" class="Upload__gbif-selected">
          <input type="hidden" name="gbif_id" :value="gbifData[0].id">
          <i>{{ gbifData[0].name }}</i> {{ gbifData[0].details }}
        </div>
        <ul v-else class="Upload__gbif-list">
          <li v-for="entry in gbifData" :key="entry.id">
            <label>
              <input type="radio" name="gbif_id" :value="entry.id" v-model="gbifSelected" @click="selectGbifSpecies(entry)">
              <i>{{ entry.name }}</i> {{ entry.details }}
            </label>
          </li>
        </ul>
        <fieldset>
          <legend><span class="Upload__section-title Upload__section-head">Specimen</span> - Please enter relevant specimen information</legend>
          <TextInput class="Upload__form-label" name="alt_name" :data="form.alt_name">Alt. Name</TextInput>
          <TextInput class="Upload__form-label" name="specimen_location" :data="form.specimen_location">Specimen Location</TextInput>
          <TextInput class="Upload__form-label" name="specimen_id" :data="form.specimen_id">Specimen ID</TextInput>
          <TextInput class="Upload__form-label" name="specimen_url" :data="form.specimen_url">Specimen URL</TextInput>
        </fieldset>
        <TextInput type="textarea" name="description" :data="form.description">
          <h2 class="Upload__section-title Upload__section-head">Description</h2>
        </TextInput>
        <fieldset>
          <legend class="Upload__section-head"><span class="Upload__section-title Upload__section-head">Publications</span> - Assign any relevant publications to the scan</legend>
          <div class="Upload__tabs">
            <button type="button" @click="myPubs=true" :class="pubsTabClass(myPubs)">My Pubs</button>
            <button type="button" @click="myPubs=false" :class="pubsTabClass(!myPubs)">All Pubs</button>
          </div>
          <div class="SelectViewer Upload__tabs-content">
            <div class="ListSearch">
              <div class="ListSearch__search Search">
                <input type="text" name="pub_query" class="Search__input"  @keyup="pubSearch" :placeholder="myPubs ? 'Search My Publications' : 'Search Publications'" autocomplete="off"/>
              </div>
              <ul class="Upload__listbox">
                <li v-for="pub in pubSearchResults" :key="pub.id">
                  <input class="Upload__checkbox" type="checkbox" :value="pub.id" :id="'pub' + pub.id" v-model="selectedPubIds">
                  <label class="Upload__result" :for="'pub' + pub.id">{{ pub.title }}</label>
                </li>
              </ul>
            </div>
            <ul class="Upload__listbox">
              <li v-for="{id, title} in selectedPubs" :key="id">
                <input class="Upload__checkbox" name="publications" type="checkbox" :value="id" :id="'sel-pub' + id" v-model="selectedPubIds">
                <label class="Upload__result" :for="'sel-pub' + id">{{ title }}</label>
              </li>
            </ul>
          </div>
        </fieldset>
      </div>
      <div class="Upload__column">
        <div class="Upload__section-head">
          <span class="Upload__section-title Upload__section-head">Categories</span> - Assign the relevant tags to this entry. At least one catagory in each of Geologic Age, Elements and Ontologic Age is required.
        </div>

        <fieldset>
          <legend class="Upload__form-label">Geologic Age</legend>
          <div class="Upload__listbox">
            <Tree :items="form.geologic_age.choices" #node="option" childKey="children" class="Upload__tree">
              <li>
                <input type="checkbox" class="Upload__checkbox" name="geologic_age" :value="option.id" :id="'geo-age' + option.id" :checked="(form.geologic_age.data || [] ).some(tag => option.id===tag.id)">
                <label :for="'geo-age' + option.id">{{ option.name }}</label>
                <component :is="option.children" />
              </li>
            </Tree>
          </div>
          <Errors :errors="form.geologic_age.errors" />
        </fieldset>

        <fieldset>
          <legend class="Upload__form-label">Ontogenic Age</legend>
          <ul class="Upload__listbox">
            <li v-for="option in form.ontogenic_age.choices" :key="option.id">
              <input type="checkbox" class="Upload__checkbox" name="ontogenic_age" :value="option.id" :id="'onto-age' + option.id" :checked="(form.ontogenic_age.data || [] ).some(tag => option.id===tag.id)">
              <label :for="'onto-age' + option.id">{{ option.name }}</label>
            </li>
          </ul>
          <Errors :errors="form.ontogenic_age.errors" />
        </fieldset>

        <fieldset>
          <legend class="Upload__form-label">Elements</legend>
          <div class="Upload__listbox">
            <Tree :items="form.elements.choices" #node="option" childKey="children" class="Upload__tree">
              <li>
                <input type="checkbox"  class="Upload__checkbox" name="elements" :value="option.id" :id="'elements' + option.id" :checked="(form.elements.data || [] ).some(tag => option.id===tag.id)">
                <label :for="'elements' + option.id">{{ option.name }}</label>
                <component :is="option.children" />
              </li>
            </Tree>
          </div>
          <Errors :errors="form.elements.errors" />
        </fieldset>
      </div>
      <div class="Upload__submit">
        <div>
          <input type="checkbox" class="Upload__checkbox" name="published" :checked="form.published.data" id="submit">
          <label for="submit">Publish</label>
        </div>
        <Button big>Save</Button>
      </div>
    </form>
  </div>
</template>

<script>
import Tree from '../tree.js';
import CtmViewer from '../CtmViewer';
import Upload3D from './Upload3D';
import { Button, TextInput, Errors, Delete } from '../forms';

const xhrUpload = (form, progress) => {
    const formData = new FormData(form);
    const xhr = new XMLHttpRequest()
    xhr.open('POST', form.action)
    xhr.setRequestHeader('Accept', 'application/json')
    const ready = new Promise((res, rej) => {
        xhr.onload = () => res(xhr);
        xhr.onerror = rej
    });

    xhr.upload.onprogress = function (event) {
        if (event.lengthComputable) {
            progress(Math.round((event.loaded / event.total) * 100))
        }
    }

    xhr.send(formData);

    return ready;
}

export default {
  name: 'Upload',
  props: [
    "error",
  ],
  data() {
    const data = this.$route.meta.data;
    const pubSearchResults = data.form.publications.choices;
    const publications = pubSearchResults.concat(data.scan.publications).reduce((o, pub) => Object.assign(o, { [pub.id]: pub }), {});
    const gbifData = (data.scan && data.scan.gbif_id) ? [{
      id: data.scan.gbif_id,
      name: data.scan.scientific_name,
      details: ''
    }] : [];
    const gbifSelected = data.scan && data.scan.gbif_id;

    return {
      progress: null,     // Upload progress of the model file
      gbifData    ,       // List of GBIF search results
      gbifSelected,       // Selected GBIF result
      stillName: '',      // Contents of the Still Name text input
      data,               // Data returned from the database
      myPubs: true,       // Search only for publications created by current user
      pubSearchResults,   // List of results for publication search
      publications,       // Object containing all publications, keyed by ID
      selectedPubIds: (data.form.publications.data || []).map(pub => pub.id), // Array of selected publication IDs
      form: data.form,
      scan: data.scan,
      csrf: data.csrf_token
    };
  },
  mounted(){
    if (this.scan) {
      this.searchGbif(this.scan.scientific_name)
    }
  },
  watch:{
    '$route.meta'(meta){
      this.form = meta.data.form
      this.scan = meta.data.scan
    },
    /* When we switch the publications tab, empty the list of search results until the user types */
    myPubs(){
      this.pubSearchResults = [];
    }
  },
  computed: {
    /**
     * List of selected pub
     */
    selectedPubs(){
      return this.selectedPubIds.map(id => this.publications[id])
    },
    stills() {
      return this.scan ? this.scan.stills : [];
    },
    formAction(){
      return this.scan ? this.$router.resolve({ name: 'edit-scan', params: this.scan }).href : '';
    }
  },
  methods: {
    async searchGbif(term) {
      if(!term) return;

      term = encodeURIComponent(term);
      const res = await fetch(`//api.gbif.org/v1/species/suggest?q=${term}&datasetKey=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c&rank=SPECIES`);
      const results = await res.json();
      this.gbifData = results.map(
        entry => ({
          id: entry.key,
          name: entry.canonicalName,
          details: `${entry.scientificName.replace(entry.canonicalName, '')} (${ entry.kingdom })`
        })
      );
    },
    /**
     * Automatically fill out the name field when user selects a GBIF item
     */
    selectGbifSpecies(species) {
      this.form.scientific_name.data = species.name;
    },
    async submit({ target }){
        const data = new FormData(target);
        const res =  await fetch(target.action, {
            method: 'POST',
            headers: { accept: 'application/json' },
            body: data
        });
        const url = res.url.replace(new URL(res.url).origin, '');
        this.$router.replace(url);
        const json = await res.json();
        this.form = json.form;
        window.scrollTo(0 ,0);
    },
    /**
     * Delete a still by its attachment id
     */
    async removeStill(id){
      const res =  await fetch(`/stills/${id}/`, {
        method: 'DELETE',
        headers: { accept: 'application/json' }
      });
      const json = await res.json();
      this.scan = json.scan;
    },
    async captureStill(){
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
      const res = await fetch(this.formAction, { method: 'POST', headers: { 'accept': 'application/json' }, body: data });
      const json = await res.json();
      this.scan = json.scan;
      this.stillName = '';
    },
    async upload(form){
        const { responseText } = await xhrUpload(form, p => this.progress = p);
        const { scan } = JSON.parse(responseText);
        this.scan = scan;
    },
    async pubSearch(event) {
        const query = encodeURIComponent(event.target.value);
        const mine = this.myPubs ? '&mine' : '';
        const res = await fetch(`/publications?title=${query}${mine}`, { headers: { accept: 'application/json' } });
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
    pubsTabClass(active){
      return {
        'Upload__tab': true,
        'Upload__tab--active': active
      }
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
}
</script>

<style>
.Upload {
  grid-column-start: 1;
  grid-column-end: 4;
  grid-template-areas: ".       . title  "
                       "sidebar . upload "
                       "sidebar . details"
                       "sidebar . .      ";
  counter-reset: section;
}

.Upload__title {
  grid-area: title;
  text-transform: uppercase;
}

.Upload__upload {
  grid-area: upload;
}

.Upload__details {
  grid-area: details;
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-column-gap: 30px;
}

.Upload__submit {
  grid-column-end: span 2;
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 66%;
  margin: 40px 0;
}

.Upload__section-head {
  margin: 30px 0 15px;
}

.Upload__section-title {
  color: #096;
  font-size: 12px;
  font-weight: bold;
  font-family: 'Supria Sans W01 Bold', Helvetica, Arial, sans-serif;
  text-transform: uppercase;
}

.Upload__section-title::before {
  counter-increment: section;
  content: counter(section) ". " ;
}

.Upload__form-label {
  display: block;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  font-size: 14px;
  color: #666;
  margin: 15px 0 5px;
}

.Upload fieldset {
    border: none;
    padding: 0;
    margin: 0;
}

.Upload__stills {
  grid-area: sidebar;
  font-size: 12px;
  margin: 0 10px;
}

.Upload__still {
  display: flex;
  flex-direction: column;
  padding: 10px;
}

.Upload__still-capture-name {
  display: flex;
  margin: 5px 0;
  align-items: flex-end;
  font-size: 12px;
}

.Upload__still-image {
    max-width: 100%;
}

.Upload__still-name {
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  color: #666;
  margin-top: 5px;
}

.Search {
    border: 1px solid #666;
    width: 100%;
    display: flex;
}

.Search__input {
    border: 0;
    flex-grow: 1;
    padding: 5px;
    font-family: 'Supria Sans W01 Regular', Helvetica, Arial, sans-serif;
    font-size: 12px;
    color: #666;
}

.ListSearch__search {
    border-bottom: none;
}

.Upload__listbox {
    border: 1px solid #666;
    min-height: 100px;
    padding: 10px;
    list-style: none;
    margin: 0;
    font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
    color: #666;
    font-size: 12px;
}

.Upload__checkbox:not(:last-child) {
  position: absolute;
  z-index: -1;
  opacity: 0;
}

.Upload__checkbox + label {
  cursor: pointer;
  display: block;
  background: url('/static/tick-box.png') no-repeat;
  background-position: left 2px;
  padding: 0 0 0 15px;
}

.Upload__checkbox:checked + label {
  background-image: url('/static/tick-box-selected.png');
}

.Upload__checkbox:focus + label {
  outline: 1px dotted;
}

.Upload__result {
  padding-bottom: 5px;
}

.SelectViewer {
    display: flex;
    margin: -7.5px;
}

.SelectViewer > * {
    flex-basis: 50%;
    margin: 7.5px;
}

.Upload__tab {
  cursor: pointer;
  font-weight: bold;
  background: none;
  margin-bottom: -1px;
  margin-left: 10px;
  font-size: 14px;
  border: 1px solid #666;
  padding: 7px 65px;
  display: inline-block;
  text-transform: uppercase;
  font-family: 'Supria Sans W01 Bold', Arial, Helvetica, sans-serif;
  color: #ccc;
}

.Upload__tab--active {
  border-bottom: 1px solid #fff;
  color: #096;
}

.Upload__tabs {
  border-bottom: 1px solid #666;
  text-align: center;
}

.Upload__tabs-content {
  padding: 20px 15px;
}

.Upload__tree {
  list-style: none;
  margin: 0;
  padding: 0;
}

.Upload__tree .Upload__tree {
  padding-left: 15px;
}

.Upload__gbif-selected {
  font-size: 12px;
  color: #666;
  padding: 5px 0 15px;
}

.Upload__gbif-list {
  list-style: none;
  padding: 5px 0 15px;
  margin: 0;
  font-size: 12px;
}

.Upload__gbif-list input {
  margin: 0 5px 0 0;
  vertical-align: middle;
}

.Upload__gbif-list label {
  padding: 5px;
  display: block;
}

.Upload__gbif-list label:hover {
  background: #ccc;
  cursor: pointer;
}
</style>
