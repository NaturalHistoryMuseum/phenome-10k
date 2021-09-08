<template>
  <ul :class="classes" v-if="!modal">
    <li v-for="error in errors" :key="error">
      {{ error.message || error }}
    </li>
  </ul>
  <div :class="classes" v-else @click.self="dismiss" v-show="!dismissed">
    <button :class="$style.close" @click="dismiss" type="button">Close</button>
    <iframe :class="$style.iframe" v-for="error in errors" :key="error" :srcdoc="error.message || error" />
  </div>
</template>

<script>
export default {
  name: 'FormErrors',
  props: ['errors'],
  data: () => {
    return {
      dismissed: false
    };
  },
  methods: {
    dismiss() {
      this.dismissed = true;
    }
  },
  computed: {
    modal() {
      return this.errors.some(e => typeof e === 'string' && e[0] === '<');
    },
    classes() {
      let cssClasses = {};
      cssClasses[this.$style.main] = true;
      cssClasses[this.$style.modal] = this.modal;
      cssClasses[this.$style.list] = !this.modal;
      return cssClasses;
    }
  },
  watch: {
    errors() {
      this.dismissed = false;
    }
  }
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

.main {
  margin: 0;
  padding: 0;

  & li {
    color: $palette-error;
  }
}

.list {
  list-style: none;
}

.modal {
  background: change-color($palette-grey-0, $alpha:0.9);
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  width: 75vw;
  height: 75vh;
  margin: auto;
  overflow: auto;
  display: grid;
  grid-gap: 10px;
  padding: 20px;
  grid-template-rows: max-content;
}

.close {
  justify-self: end;
  @include font-body;
  font-size: $small-font-size;
}

.iframe {
  background: white;
  border: none;
  height: 100%;
  width: 100%;
}
</style>
