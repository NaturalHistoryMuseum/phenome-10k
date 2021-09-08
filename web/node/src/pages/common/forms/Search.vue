<template>
  <form :class="$style.main">
    <label>
      <slot>Search:</slot>
      <input :class="$style.input" type="search" :name="name" :value="value" @input="input" />
    </label>
    <Button :class="$style.button">🔎&#xFE0E;</Button>
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
    input($event) {
      this.$emit('input', $event.target.value);
    }
  }
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

.main {
  display: flex;
  height: 2em;
}

.input {
  border: 1px solid $palette-grey-4;
  border-right: none;
  border-radius: 15px 0 0 15px;
  padding: 3px 10px;
  margin-left: 10px;
  width: 200px;
  height: 100%;
  @include font-body;
  font-size: $small-font-size;
}

.button {
  display: inline-block;
  border-radius: 0 15px 15px 0;
  width: 50px;
  padding: 0;
}
</style>
