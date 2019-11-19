<template>
  <ul :class="classes" v-if="!modal">
    <li v-for="error in errors" :key="error">
      {{ error.message || error }}
    </li>
  </ul>
  <div :class="classes" v-else @click.self="dismiss" v-show="!dismissed">
    <button class="Errors__close" @click="dismiss" type="button">Close</button>
    <iframe class="Errors__iframe" v-for="error in errors" :key="error" :srcdoc="error.message || error" />
  </div>
</template>

<style>
.Errors {
  margin: 0;
  padding: 0;
}

.Errors--list {
  list-style: none;
}

.Errors--modal {
  background: white;
  position: fixed;
  top: 0;
  width: 100%;
  left: 0;
  height: 100%;
  background: #0009;
  overflow: auto;
  display: grid;
  padding: 5%;
  grid-template-rows: max-content;
}

.Errors__close {
  justify-self: end;
}

.Errors li {
  color: red;
}
</style>

<script>
export default {
  name: 'FormErrors',
  props: ['errors'],
  data: () => {
    return {
      dismissed: false
    }
  },
  methods: {
    dismiss(){
      this.dismissed = true;
    }
  },
  computed: {
    modal(){
      return this.errors.some(e => typeof e === 'string' && e[0] === '<');
    },
    classes(){
      return {
        'Errors': true,
        'Errors--modal': this.modal,
        'Errors--list': !this.modal,
      }
    }
  },
  watch: {
    errors(){
      this.dismissed = false;
    }
  }
}
</script>
