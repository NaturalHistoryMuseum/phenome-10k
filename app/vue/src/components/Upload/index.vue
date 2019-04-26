<template>
  <form class="Upload Subgrid" :action="formAction" method="post" @submit.prevent="submit" enctype="multipart/form-data" novalidate>
    <h1 class="Upload__title">{{ scan ? "Edit: " + scan.scientific_name : "Upload New" }}</h1>
    <input type="hidden" name="csrf_token" :value="csrf">
    <span v-if="error" class="error">[{{ error }}]</span>
    <div class="Upload__upload">
      <h2 class="Upload__section-title">1. Browse and preview STL file</h2>
      <CtmViewer v-if="scan && scan.ctm" ref="canvas" :src="scan.ctm" height=400px width=500px />
      <Upload3D v-else @change="upload" :progress="progress" :errors="form.file.errors"></Upload3D>
    </div>
    <span class="Upload__stills">
      <span class="Upload__section-title">2. Take Stills</span> - Move image into appropriate position and click the button below (Minimum of 1 snapshot image, maximum of 6 images).

      <div class="Upload__still-capture-name">
        <label>Label: <input class="Upload__form-input" v-model="stillName"></label>
        <button type="button" class="Upload__form-button" @click="captureStill">Capture</button>
      </div>
      <div v-for="error in form.stills.errors" :key="error">{{ error }}</div>

      <div v-for="{ name, file, id } in stills" :key="file" class="Upload__still">
        <button type="button" @click="removeStill(id)" class="Upload__remove-still">Remove Image ❌</button>
        <img :src="file" class="Upload__still-image" />
        <div class="Upload__still-name">{{ name }}</div>
      </div>
    </span>
    <div class="Upload__details">
      <TextInput name="scientific_name" :data="form.scientific_name" @keyup="e => searchGbif(e.target.value)">
        <h2 class="Upload__section-title">3. Scientific Name</h2>
      </TextInput>
      <ul>
        <li v-for="entry in gbifData" :key="entry.key"><label><input type="radio" name="gbif_id" :value="entry.key" v-model="gbifSelected"><i>{{ entry.canonicalName }}</i> {{ entry.scientificName.replace(entry.canonicalName, '') }} ({{ entry.kingdom }})</label></li>
      </ul>
      <fieldset>
        <legend><span class="Upload__section-title">4. Specimen</span> - Please enter relevant specimen information</legend>
        <TextInput name="alt_name" :data="form.alt_name">Alt Name</TextInput>
        <TextInput name="specimen_location" :data="form.specimen_location">Specimen Location</TextInput>
        <TextInput name="specimen_id" :data="form.specimen_id">Specimen ID</TextInput>
      </fieldset>
      <FormField :errors="form.description.errors">
        <h2 class="Upload__section-title">6. Description</h2>
        <textarea name="description" :value="form.description.data" class="Upload__form-input" />
      </FormField>
      <fieldset>
        <legend><span class="Upload__section-title">7. Publications</span> - Assign any relevant publications to the scan</legend>
        <div class="SelectViewer">
          <div class="ListSearch">
            <div class="ListSearch__search Search">
              <input type="text" name="pub_query" class="Search__input"  @keyup="pubSearch" />
              <button name="pub_search" :value="form.pub_search.data" class="Search__submit">Search</button>
            </div>
            <div name="publications_search" class="ListSearch__results">
              <ul>
                <li v-for="pub in pubList" :key="pub.id"><input name="publications_search" type="checkbox" :value="pub.id">{{ pub.title }}</li>
              </ul>
            </div>
          </div>
          <div name="publications" class="ListSearch__results">
            <ul>
              <li v-for="pub in savedPublications" :key="pub.id"><input name="publications" type="checkbox" :value="pub.id">{{ pub.title }}</li>
            </ul>
          </div>
        </div>
      </fieldset>
      <p>8. Categories - Assign the relevant tags to this entry. At least one catagory in each of Taxonomy, Geologic Age, Elements and Ontologic Age is required.</p>

      <fieldset>
        <legend>Geologic Age</legend>
        <Tree :items="form.geologic_age.choices" #node="option" childKey="children">
          <li><label><input type="checkbox" name="geologic_age" :value="option.id" :checked="(form.geologic_age.data || [] ).some(tag => option.id===tag.id)">{{ option.name }}</label></li>
        </Tree>
        <div v-for="error in form.geologic_age.errors" :key="error">{{ error }}</div>
      </fieldset>

      <fieldset>
        <legend>Ontogenic Age</legend>
        <ul>
          <li v-for="option in form.ontogenic_age.choices" :key="option.id"><label><input type="checkbox" name="ontogenic_age" :value="option.id" :checked="(form.ontogenic_age.data || [] ).some(tag => option.id===tag.id)">{{ option.name }}</label></li>
        </ul>
        <div v-for="error in form.ontogenic_age.errors" :key="error">{{ error }}</div>
      </fieldset>

      <fieldset>
        <legend>Elements</legend>
        <ul>
          <li v-for="option in form.elements.choices" :key="option.id"><label><input type="checkbox" name="elements" :value="option.id" :checked="(form.elements.data || [] ).some(tag => option.id===tag.id)">{{ option.name }}</label></li>
        </ul>
        <div v-for="error in form.elements.errors" :key="error">{{ error }}</div>
      </fieldset>
      <label><input type="checkbox" name="published" :checked="form.published.data"> Publish</label>
      <p><button class="Upload__form-button">Submit</button></p>
    </div>
  </form>
</template>

<script>
import Tree from '../tree.js';
import CtmViewer from '../CtmViewer';
import Upload3D from './Upload3D';

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

const FormField = {
  name: 'FormField',
  props: [ 'errors' ],
  render(h){
      return h('label', [
          this.$slots.default,
          ...this.errors.map(
              error => h('div', [ error ])
          )
      ])
  }
}

const TextInput = {
    inheritAttrs: false,
    props: ['label', 'data'],
    data(){
        return {
            initialValue: this.data.data
        }
    },
    render(h) {
        return h(FormField, { props: { errors: this.data.errors } }, [
            this.$slots.default,
            h('input', {
                class: {
                  "Upload__form-input": true
                },
                attrs: {
                  ...this.$attrs,
                  value: this.initialValue
                },
                on: this.$listeners
            })
        ])
    }
}

export default {
  name: 'Upload',
  props: [
    "error",
  ],
  data() {
    return {
      progress: null,
      pubList: [],
      gbifData: [],
      gbifSelected: null,
      stillName: '',
      data: this.$route.meta.data
    };
  },
  watch:{
    '$route.meta'(meta){
      this.data = meta.data;
    },
  },
  computed: {
    scan: {
      get(){
        return this.data.scan;
      },
      set(value){
        this.data.scan = value;
      }
    },
    csrf(){
      return this.data.csrf_token;
    },
    form: {
      get(){
        return this.data.form;
      },
      set(val) {
        this.data.form = val;
      }
    },
    stills() {
      return this.scan ? this.scan.stills : [];
    },
    formAction(){
      return this.scan ? this.$router.resolve({ name: 'edit-scan', params: this.scan }).href : '';
    },
    savedPublications() {
      const scanPubs = this.scan ? this.scan.publications : [];
      const formPubIds = this.form.publications.data || [];
      const pubsList = [...scanPubs, ...this.pubList];
      return formPubIds.map(id => pubsList.find(pub => pub.id === id) || { id, title: id });
    }
  },
  methods: {
    async searchGbif(term) {
        const res = await fetch(`//api.gbif.org/v1/species/suggest?q=${term}&datasetKey=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c&rank=SPECIES`);
        const results = await res.json();
        this.gbifData = results;
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
        const query = event.target.value;
        const res = await fetch(`/publications?title=${query}`, { headers: { accept: 'application/json' } });
        this.pubList = await res.json();
    }
  },
  components: {
      TextInput,
      FormField,
      Upload3D,
      CtmViewer,
      Tree
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
}

.Upload__title {
  grid-area: title;
  color: #096;
  font-weight: normal;
  font-size: 24px;
  font-family: 'Neo Sans W01', Helvetica, Arial, sans-serif;
  text-transform: uppercase;
  margin-bottom: 40px;
}

.Upload__upload {
  grid-area: upload;
}

.Upload__details {
  grid-area: details;
}

.Upload__section-title {
    color: #096;
    font-size: 12px;
    font-weight: bold;
    font-family: 'Supria Sans W01 Bold', Helvetica, Arial, sans-serif;
    text-transform: uppercase;
    margin: 30px 0 15px;
}

.Upload__form-input {
    border: 1px solid #666;
    display: block;
    padding: 5px;
    font-family: 'Supria Sans W01 Regular', Helvetica, Arial, sans-serif;
    font-size: 12px;
    color: #666;
    width: 100%;
}

.Upload__form-button {
  appearance: none;
  display: block;
  text-align: center;
  color: #fff;
  text-transform: uppercase;
  background: #096;
  padding: 6px 7px;
  font-family: 'Supria Sans W01 Bold', Arial, Helvetica, sans-serif;
  font-size: 12px;
  border: none;
  font-weight: bold;
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

.Upload__remove-still {
  appearance: none;
  border: none;
  background: none;
  color: #666;
  font-size: 10px;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  align-self: flex-end;
  cursor: pointer;
  margin: 0 0 5px;
  padding: 0;
}

.Upload__remove-still:hover {
  text-decoration: underline;
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

.Search__submit {
    border: 0;
}


.ListSearch__search {
    border-bottom: none;
}

.ListSearch__results {
    border: 1px solid #666;
    min-height: 100px;
    padding: 10px;
    list-style: none;
    margin: 0;
    font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
    color: #666;
    font-size: 12px;
}

.ListSearch__results li {
    display: flex;
    flex-direction: row-reverse;
    justify-content: flex-end;
    align-items: flex-start;
    margin: 2.5px 0;
}

.ListSearch__results input {
    border: 1px solid #096;
}


.SelectViewer {
    display: flex;
}

.SelectViewer > * {
    flex-basis: 50%;
    margin: 7.5px;
}
</style>
