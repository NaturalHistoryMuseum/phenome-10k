<template>
  <div :class="$style.main" @dragover="dragOver" @dragleave="dragEnd" @drop="drop">
    <label :class="labelClass" v-show="progress == null && status == null">
      <h1 :class="$style.dropText">Drop scan or zip here</h1>
      <div :class="$style.or">or</div>
      <div :class="$style.select">Select File</div>
      <input type="file" name="file" @change="fileChange" :class="$style.file" />
    </label>
    <div v-if="progress != null || status != null" :class="$style.progress">
      <progress :class="$style.progressBar" :value="progress || 100" max="100"></progress>
      <div :class="$style.progressText">
        {{ status || (progress + '%') }}
      </div>
    </div>
    <Errors :errors="errors" />
  </div>
</template>

<script>
import Errors from '../../common/forms/Errors';

export default {
  name: 'Upload3D',
  components: {
    Errors
  },
  props: ['progress', 'status', 'errors'],
  data() {
    return {
      dragging: false
    };
  },
  computed: {
    labelClass() {
      const cls = [this.$style.input];
      if (this.dragging) {
        cls.push(this.$style['input--hovered']);
      }
      return cls.join(' ');
    }
  },
  methods: {
    fileChange(e) {
      this.uploadFile(e.target.form);
    },
    dragOver(e) {
      e.preventDefault();
      this.dragging = true;
    },
    dragEnd(e) {
      e.preventDefault();
      this.dragging = false;
    },
    drop(e) {
      e.preventDefault();
      const input = e.target.control;
      input.files = e.dataTransfer.files;
      this.uploadFile(e.target.form);
    },
    uploadFile(form) {
      if (!form) {
        this.dragging = false;
        return;
      }
      this.$emit('change', form);
    }
  }
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

.main {
  width: 100%;
  height: 900px;
}

.input {
  height: 100%;
  background: $palette-grey-7;
  display: grid;
  align-content: center;
  justify-items: center;
}

.input--hovered {
  border: 3px dashed $palette-grey-3;
}

.dropText {
  text-transform: uppercase;
}

.select {
  display: block;
  width: 110px;
  background: $palette-grey-6;
  font-size: $small-font-size;
  color: $palette-grey-1;
  margin: 0 auto;
  padding: 5px 0;
  border: 1px solid $palette-grey-3;
  text-align: center;
}

.file {
  width: 0;
}

.or {
  font-size: 12px;
  font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
  color: #666;
  line-height: 9px;
  margin: 15px 0;
}

.progress {
  height: 100%;
  width: 100%;
  display: grid;
  align-content: stretch;
  justify-items: center;
  grid-template-areas: 'content';
}

.progressBar {
  height: 100%;
  width: 100%;
  grid-area: content;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;

  &::-webkit-progress-value, &::-moz-progress-bar {
    background-color: $palette-primary;
  }
}

.progressText {
  @include font-heading;
  grid-area: content;
  font-size: 4em;
  color: $palette-grey-1;
  align-self: center;
}
</style>
