<template>
  <button v-bind="$attrs" v-on="$listeners" :class="{ [$style.main]: true, [$style.big]: 'big' in $attrs }">
    <slot />
  </button>
</template>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

.main {
  appearance: none;
  display: block;
  text-align: center;
  color: #fff;
  text-transform: uppercase;
  background: $palette-primary;
  padding: 6px 7px;
  font-size: $small-font-size;
  border: none;
  font-weight: bold;
  @include font-heading;
}

.big {
  padding: 10px 60px;
  font-size: 14px;
}
</style>
