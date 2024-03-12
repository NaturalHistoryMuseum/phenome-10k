<template functional>
  <button :class="$style.main" v-bind="props" v-on="listeners">
    <span><slot /></span>
    <span>❌</span>
  </button>
</template>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

.main {
  appearance: none;
  border: none;
  background: none;
  color: $palette-grey-3;
  font-size: $small-font-size;
  @include font-body;
  justify-self: end;
  cursor: pointer;
  margin: 0;
  padding: 5px;

  &:hover {
    background: $palette-grey-7;
    color: $palette-grey-2;
    transition: all 0.2s;
  }

  & > * {
    padding-left: 5px;
  }
}
</style>
