<template>
  <form method="post" enctype="multipart/form-data" :class="$style.main">
    <div :class="$style.title">
      <h1>{{ publication ? 'Edit Publication' : 'Upload New Publication' }}</h1>
    </div>

    <div :class="['Body__content', $style.sectionGrid]">
      <div :class="$style.section">
        <div :class="$style.sectionHead">
          <h2 :class="$style.sectionTitle">Information</h2>
        </div>
        <input type="hidden" name="csrf_token" :value="csrf_token">
        <TextInput name="title" :data="form.title" :class="$style.field"
                   :labelClass="[$style.required, $style['required--first']]" type="text">
          Title
        </TextInput>
        <TextInput name="pub_year" :data="form.pub_year" :class="$style.field" :labelClass="$style.required"
                   type="text">
          Publication Year
        </TextInput>
        <TextInput name="authors" :data="form.authors" :class="$style.field" :labelClass="$style.required" type="text">
          Authors
        </TextInput>
        <TextInput name="journal" :data="form.journal" :class="$style.field" :labelClass="$style.required" type="text">
          Journal, Volume and Page
        </TextInput>
        <TextInput type="textarea" rows="12" name="abstract" :data="form.abstract" :class="$style.field"
                   :labelClass="$style.required">
          Abstract
        </TextInput>
        <TextInput name="link" placeholder="http://" :data="form.link" :class="$style.field" type="text">
          URL Link
        </TextInput>
      </div>
      <div :class="$style.section">
        <div :class="$style.sectionHead">
          <h2 :class="$style.sectionTitle">Upload PDFs</h2>
        </div>
        <ul :class="$style.fileList">
          <li v-for="file in files" :key="file.id">
            <a :href="file.file" :class="$style.label">{{ file.filename }}</a>
            <Delete name="delete" type="button" @click="removeFile(file.id)">Remove</Delete>
          </li>
        </ul>
        <label :class="$style.fileInput">
          <input type="file" multiple accept=".pdf" name="files" ref="fileInput" @change="selectFiles"/>
          <span :class="$style.button">Browse</span>
          <span :class="$style.text">{{ selectedFiles.length === 1 ? selectedFiles[0].name : `${ selectedFiles.length || 'No' } files selected.` }}</span>
        </label>
        <Errors :errors="form.files.errors" />
        <div :class="$style.controls">
          <Button big>Publish</Button>
        </div>
      </div>
    </div>
  </form>
</template>

<script>
import { Button, Delete, Errors, TextInput } from '../common/forms';

export default {
  components: {
    TextInput,
    Errors,
    Button,
    Delete
  },
  data() {
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
    async removeFile(id) {
      const res = await fetch(`/remove-pub-file/${ id }`, {
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
  mounted() {
    this.selectedFiles();
  }
};
</script>

<style module lang="scss">
@import '../common/styles/edit';
@import 'scss/palette';
@import 'scss/fonts';

.required {
  &::after {
    content: '*';
    font-size: 0.8em;
    padding-left: 5px;
  }

  &--first::after {
    content: '* Required';
  }
}

textarea {
  resize: vertical;
}

.fileInput {
  display: flex;
  height: 2em;

  .text {
    border: 1px solid $palette-grey-4;
    border-left: none;
    padding: 3px 10px;
    width: 100%;
    height: 100%;
    font-size: $small-font-size;
    line-height: 1.7em; // same as default but apparently needs to be set again
  }

  .button {
    display: inline-block;
    min-width: 50px;
    padding: 0 20px;
    background: $palette-primary;
    text-align: center;
    color: #fff;
    text-transform: uppercase;
    font-size: $small-font-size;
    border: none;
    font-weight: bold;
    @include font-heading;
  }

  input {
    display: none;
  }
}

.controls {
  margin-top: 70px;
  display: flex;
  justify-content: center;
}

.fileList {
  border-top: 1px solid #ebebeb;
  margin: 0 0 30px;
  padding: 0;

  & li {
    border-bottom: 1px solid #ebebeb;
    padding: 10px 5px;
    display: flex;
    justify-content: space-around;
  }
}
</style>


