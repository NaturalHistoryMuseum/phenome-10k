<template>
  <form :class="$style.main">
    <label :class="$style.label">
      <span :class="$style.labelText"><slot>Search:</slot></span>
      <input
        :class="$style.input"
        type="search"
        :name="name"
        :value="value"
        @input="input"
      />
    </label>
    <Button :class="$style.button">🔎&#xFE0E;</Button>
  </form>
</template>

<script>
import Button from './Button';

export default {
  components: {
    Button,
  },
  props: ['value', 'name'],
  methods: {
    input($event) {
      this.$emit('input', $event.target.value);
    },
  },
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';
@import 'scss/vars';

.main {
  display: grid;
  grid-template-columns: auto minmax(200px, 300px) 1fr;
  grid-auto-rows: 2em;
  margin-right: 2em;
}

@media (max-width: $small-screen) {
  .main {
    grid-template-columns: 1fr auto;
  }

  .labelText {
    grid-column: span 2;
  }
}

.label {
  display: contents;
}

.labelText {
  margin-right: 1em;
  text-transform: uppercase;
  color: $palette-grey-2;
  font-size: $small-font-size;
}

.input {
  border: 1px solid $palette-grey-4;
  border-right: none;
  border-radius: 15px 0 0 15px;
  padding: 3px 10px;
  height: 100%;
  width: 100%;
  justify-self: end;
  @include font-body;
  font-size: $small-font-size;
}

.button {
  display: inline-block;
  border-radius: 0 15px 15px 0;
  width: 50px;
  padding: 0;
  justify-self: start;
}
</style>
