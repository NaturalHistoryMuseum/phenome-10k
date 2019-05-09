<template>
  <form class="Search">
    <label><slot>Search:</slot><input class="Search__input" type="search" :name="name" :value="value" @input="input" /></label><Button class="Search__button">🔎&#xFE0E;</Button>
  </form>
</template>

<script>
import Button from './Button';

export default {
  components: {
    Button
  },
  props: ['value', 'name'],
  methods: {
    input($event){
      this.$emit('input', $event.target.value);
    }
  }
}
</script>

<style>
.Search {
  display: flex;
}

.Search__input {
  border: 1px solid black;
  border-right: none;
  border-radius: 15px 0 0 15px;
  padding: 3px 10px;
  margin-left: 10px;
  width: 200px;
}

.Search__button {
  display: inline-block;
  text-shadow: 1px 1px 0.25px #FFF,
                -1px -1px 0.25px #FFF,
                1px -1px 0.25px #FFF,
                -1px 1px 0.25px #FFF;
  border-radius: 0 15px 15px 0;
  width: 50px;
  padding: 0;
}
</style>
