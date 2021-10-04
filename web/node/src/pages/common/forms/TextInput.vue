<template>
  <label>
    <div :class="labelClass">
      <slot />
    </div>
    <textarea v-if="$attrs.type === 'textarea'" :class="$style.input" v-bind="$attrs" v-on="$listeners"
              v-model="initialValue" />
    <input v-else :class="$style.input" v-bind="$attrs" v-on="$listeners" v-model="initialValue" />
    <Errors :errors="data.errors" />
  </label>
</template>

<script>
import Errors from './Errors';

export default {
  components: {
    Errors
  },
  inheritAttrs: false,
  props: ['data', 'labelClass'],
  data() {
    return {
      initialValue: this.data.data
    };
  },
  watch: {
    'data.data'(value) {
      this.initialValue = value;
    }
  }
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
