<template>
  <Tree :items="tags" #node="tag" childKey="children">
    <li :class="getFilterClass(tag.category, tag.taxonomy)">
      <router-link :to="getFilterLink(tag.category, tag.taxonomy)">{{ tag.name }}</router-link>
      <component :is="tag.children" />
    </li>
  </Tree>
</template>

<script>
import Tree from '../tree.js';

export default {
  name: 'TagTree',
  props: ['tags'],
  components: { Tree },
  methods: {
    getFilterLink(category, tag) {
      const query = Object.assign({}, this.$route.query);

      const values = new Set([].concat(query[category]))

      if(values.has(tag)) {
        values.delete(tag);
      }else{
        values.add(tag);
      }

      query[category] = Array.from(values);

      return { query };
    },
    getFilterClass(category, tag) {
      const current = this.$route.query[category];
      const categories = new Set(Array.isArray(current) ? current : [current]);
      return categories.has(tag) ? 'Library__filter-active' : '';
    }
  }
}
</script>
