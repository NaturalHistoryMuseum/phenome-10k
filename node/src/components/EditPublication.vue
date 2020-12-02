<template>
  <form method="post" enctype="multipart/form-data" class="EditPublication">
    <h1>{{ publication ? 'Edit Publication' : 'Upload New Publication' }}</h1>
    <h2 class="EditPublication__section-title">Information</h2>
    <input type="hidden" name="csrf_token" :value="csrf_token">
    <TextInput name="title" :data="form.title" class="EditPublication__field" labelClass="EditPublication__label">
      Title
      <div class="EditPublication__required">Required *</div>
    </TextInput>
    <TextInput name="pub_year" :data="form.pub_year" class="EditPublication__field" labelClass="EditPublication__label">
      Publication Year
      <div class="EditPublication__required">*</div>
    </TextInput>
    <TextInput name="authors" :data="form.authors" class="EditPublication__field" labelClass="EditPublication__label">
      Authors
      <div class="EditPublication__required">*</div>
    </TextInput>
    <TextInput name="journal" :data="form.journal" class="EditPublication__field" labelClass="EditPublication__label">
      Journal, Volume and Page
      <div class="EditPublication__required">*</div>
    </TextInput>
    <TextInput type="textarea" rows="12" name="abstract" :data="form.abstract" class="EditPublication__field" labelClass="EditPublication__label">
      Abstract
      <div class="EditPublication__required">*</div>
    </TextInput>
    <TextInput name="link" placeholder="http://" :data="form.link" class="EditPublication__field" labelClass="EditPublication__label">
      URL Link
    </TextInput>
    <h2 class="EditPublication__section-title">Upload PDFs</h2>
    <ul class="EditPublication__file-list">
      <li v-for="file in files" :key="file.id">
        <a :href="file.file" class="EditPublication__label">{{ file.filename }}</a>
        <Delete name="delete" type="button" @click="removeFile(file.id)">Remove</Delete>
      </li>
    </ul>
    <label class="EditPublication__file-input">
      <input type="file" multiple accept=".pdf" name="files" ref="fileInput" @change="selectFiles" />
      <div class="EditPublication__file-input-button">Browse</div>
      <div class="EditPublication__file-input-text">{{ selectedFiles.length === 1 ? selectedFiles[0].name : `${selectedFiles.length || 'No'} files selected.` }}</div>
    </label>
    <Errors :errors="form.files.errors" />
    <div class="EditPublication__controls">
      <Button big>Publish</Button>
    </div>
  </form>
</template>

<style>
.EditPublication {
  counter-reset: section;
}

.EditPublication__section-title {
  color: #096;
  font-family: 'Supria Sans W01 Bold', Arial, Helvetica, sans-serif;
  font-size: 12px;
  text-transform: uppercase;
  margin: 50px 0;
}

.EditPublication__section-title::before {
  counter-increment: section;
  content: counter(section) ". " ;
}

.EditPublication__label {
  color: #666;
  font-family: 'supria sans w01 regular', Arial, Helvetica, sans-serif;
  font-size: 14px;
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;
}

.EditPublication__required {
  font-size: 10px;
}

.EditPublication__field {
  display: block;
  margin-top: 20px;
}

.EditPublication__file-input {
  border: 1px solid black;
  display: flex;
}

.EditPublication__file-input input[type="file"] {
  position: absolute;
  z-index: -1;
  opacity: 0;
}

.EditPublication__file-input-button {
  background: #096;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  color: #fff;
  font-size: 11px;
  text-align: center;
  padding: 0 25px;
  vertical-align: middle;
  display: inline-block;
  line-height: 25px;
  cursor: pointer;
}

.EditPublication__file-input-text {
  font-size: 11px;
  color: #999;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  line-height: 25px;
  margin-left: 5px;
}

.EditPublication__controls {
  margin-top: 70px;
  display: flex;
  justify-content: center;
}

.EditPublication__file-list {
  border-top: 1px solid #ebebeb;
  margin: 0 0 30px;
  padding: 0;
}

.EditPublication__file-list li {
  border-bottom: 1px solid #ebebeb;
  font-family: 'Supria Sans W01 Regular';
  padding: 10px 5px;
  display: flex;
  justify-content: space-around;
}
</style>

<script>
import { TextInput, Errors, Button, Delete } from './forms';

export default {
  components: {
    TextInput,
    Errors,
    Button,
    Delete
  },
  data(){
    return {
      selectedFiles: [],
      csrf_token: this.$route.meta.data.csrf_token,
      form: this.$route.meta.data.form,
      publication: this.$route.meta.data.publication
    };
  },
  computed: {
    /**
     * List of files attached to the publication being edited
     */
    files() {
      return this.publication ? this.publication.files : [];
    }
  },
  methods: {
    /**
     * On change of file input, store list of selected files
     */
    selectFiles() {
      // input.files always has the same identity
      // copy as array so vue detects the change
      this.selectedFiles = [...this.$refs.fileInput.files];
    },
    /**
     * Delete a file by its attachment id
     */
    async removeFile(id){
      const res =  await fetch(`/remove-pub-file/${id}`, {
        method: 'DELETE',
        headers: { accept: 'application/json' }
      });
      const json = await res.json();
      this.publication = json.publication;
    }
  },
  /**
   * Fetch the selected files on mount in case input is pre-populated (e.g. page refresh)
   */
  mounted(){
    this.selectedFiles()
  }
}
</script>
