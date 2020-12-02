<template>
  <label>
    <div :class="labelClass"><slot /></div>
    <textarea v-if="$attrs.type === 'textarea'" class="TextInput__input" v-bind="$attrs" v-on="$listeners" v-model="initialValue" />
    <input v-else class="TextInput__input" v-bind="$attrs" v-on="$listeners" v-model="initialValue" />
    <Errors :errors="data.errors" />
  </label>
</template>

<style>
.TextInput__input {
    border: 1px solid #666;
    display: block;
    padding: 5px;
    font-family: 'Supria Sans W01 Regular', Helvetica, Arial, sans-serif;
    font-size: 12px;
    color: #666;
    width: 100%;
}
</style>

<script>
import Errors from './Errors';

export default {
  components: {
    Errors
  },
  inheritAttrs: false,
  props: ['data', 'labelClass'],
  data(){
    return {
      initialValue: this.data.data
    }
  },
  watch: {
    "data.data"(value){
      this.initialValue = value;
    }
  }
}
</script>
