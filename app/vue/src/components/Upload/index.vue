<template>
  <form class="Upload__form Subgrid" :action="formAction" method="post" @submit.prevent="submit" enctype="multipart/form-data" novalidate style="display:contents">
    <h1 class="Upload__title">Upload New</h1>
    <input type="hidden" name="csrf_token" :value="csrf">
    <span v-if="error" class="error">[{{ error }}]</span>
    <h2 class="Upload__section-title">1. Browse and preview STL file</h2>
    <div v-if="scan && scan.ctm" class="Subgrid" style="grid-column-start: 1; grid-column-end: 4; grid-auto-flow: dense">
      <CtmViewer ref="canvas" :src="scan.ctm" height=400px width=500px />
      <span class="Upload__stills">
        2. Take Stills - Move image into appropriate position and click the button below (Minimum of 1 snapshot image, maximum of 6 images).

        <button type="button" @click="captureStill">Capture</button>
        <div v-for="error in form.stills.errors" :key="error">{{ error }}</div>

        <img v-for="url in stillUrls" :src="url" :key="url" class="Upload__still" />
      </span>
    </div>
    <Upload3D v-else style="width: 100%; display: block;" @change="upload" :progress="progress" :errors="form.file.errors"></Upload3D>
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
    <label><input type="checkbox" name="published" :checked="form.published.data"> Publish</label>
    <p><button>Submit</button></p>
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
  inject: ['defaultData'],
  data() {
      return {
          scan: this.defaultData.scan,
          progress: null,
          stills: [],
          pubList: [],
          csrf: this.defaultData.csrf_token,
          form: this.defaultData.form,
          gbifData: [],
          gbifSelected: null
        };
  },
  computed: {
      stillUrls() {
          return [
              ...this.scan.attachments.map(a => '/' + a),
              ...this.stills.map(file => URL.createObjectURL(file))
          ]
      },
      formAction(){
        return this.scan ? `/${this.scan.id}/edit` : '';
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
    async captureStill(){
        const file = `still-${this.stills.length}.png`
        const still = await this.$refs.canvas.captureStill(file);
        this.stills.push(still);

        const data = new FormData();
        data.append('csrf_token', this.csrf);
        data.append('attachments', still, file);
        fetch(this.formAction, { method: 'POST', headers: { 'accept': 'application/json' }, body: data }).then(res => console.log(res));
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
.Upload__title {
    color: #096;
    font-weight: normal;
    font-size: 24px;
    font-family: 'Neo Sans W01', Helvetica, Arial, sans-serif;
    text-transform: uppercase;
    margin-bottom: 40px;
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

.Upload__form fieldset {
    border: none;
    padding: 0;
    margin: 0;
}

.Upload__stills {
    grid-column-start: 1;
}

.Upload__still {
    max-width: 100%;
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
