<template>
  <div class="Pagination">
    <div>Page {{ page }} of {{ total || 1 }}</div>
    <div v-if="total > 1">
      <template v-if="page > 2">
        <router-link v-bind="link(1)">1</router-link>
        …
      </template>
      <router-link v-bind="link(page - 1)" v-if="page > 1">{{ page - 1 }}</router-link>
      <router-link v-bind="link(page)">{{ page }}</router-link>
      <router-link v-bind="link(page + 1)" v-if="page < total">{{ page + 1 }}</router-link>
      <template v-if="page < total - 1">
        …
        <router-link v-bind="link(total)">{{ total }}</router-link>
      </template>
    </div>
  </div>
</template>

<style>
.Pagination {
  display: flex;
  justify-content: space-between;
  font-family: 'HelveticaNeueW01-55Roma', Arial, Helvetica, sans-serif;
  font-size: 11px;
  color: #333;
}

.Pagination__page--active {
  color: #096;
}
</style>

<script>
export default {
  props: [
    'to', // Function that returns the router-link object for a page, given page number as argument
    'page', // The current page number
    'total' // The total number of pages
  ],
  methods: {
    /**
     * Generate the props to bind to the router-link component
     */
    link(page) {
      return {
        to: this.to(page),
        class: {
          'Pagination__page': true,
          'Pagination__page--active': this.page === page
        }
      };
    }
  }
};
</script>
