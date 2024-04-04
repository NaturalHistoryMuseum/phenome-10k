<template>
  <div :class="$style.main">
    <div>Page {{ page }} of {{ total || 1 }}</div>
    <div v-if="total > 1">
      <template v-if="page > 2">
        <router-link v-bind="link(1)">1</router-link>
        …
      </template>
      <router-link v-bind="link(page - 1)" v-if="page > 1">{{
        page - 1
      }}</router-link>
      <router-link v-bind="link(page)">{{ page }}</router-link>
      <router-link v-bind="link(page + 1)" v-if="page < total">{{
        page + 1
      }}</router-link>
      <template v-if="page < total - 1">
        …
        <router-link v-bind="link(total)">{{ total }}</router-link>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  props: [
    'to', // Function that returns the router-link object for a page, given page number as argument
    'page', // The current page number
    'total', // The total number of pages
  ],
  methods: {
    /**
     * Generate the props to bind to the router-link component
     */
    link(page) {
      let cssClasses = {};
      cssClasses[this.$style.page] = true;
      cssClasses[this.$style['page--active']] = this.page === page;

      return {
        to: this.to(page),
        class: cssClasses,
      };
    },
  },
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

.main {
  display: flex;
  justify-content: space-between;
  font-size: $small-font-size;
  color: $palette-grey-2;
  padding: 2em 0;
}

.page {
  display: inline-block;
  text-align: center;
  width: 2.4em;
  height: 2.4em;
  font-weight: bold;
  border-radius: 100%;
  &--active {
    border: 2px solid $palette-primary;
  }

  &:hover {
    transition: 0.2s background-color;
    background-color: change-color($palette-grey-5, $alpha: 0.3);
  }
}
</style>
