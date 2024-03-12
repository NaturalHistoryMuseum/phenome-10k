<template>
  <label>
    <div :class="labelClass">
      <slot />
    </div>
    <textarea
      v-if="$attrs.type === 'textarea'"
      :class="$style.input"
      v-bind="$attrs"
      v-on="$listeners"
      @input="setValue"
      :value="text"
    />
    <input
      v-else
      :class="$style.input"
      v-bind="$attrs"
      v-on="$listeners"
      :value="text"
      @input="setValue"
    />
    <Errors :errors="data.errors" />
  </label>
</template>

<script>
import Errors from './Errors';

export default {
  components: {
    Errors,
  },
  inheritAttrs: false,
  props: ['data', 'labelClass'],
  data() {
    return {};
  },
  computed: {
    text() {
      return this.data.data;
    },
  },
  methods: {
    setValue(event) {
      this.$set(this.data, 'data', event.target.value);
    },
  },
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

.input {
  border: 1px solid $palette-grey-4;
  padding: 3px 10px;
  width: 100%;
  @include font-body;
  font-size: $small-font-size;

  &[type='text'] {
    height: 2 * $body-font-size;
  }
}
</style>
