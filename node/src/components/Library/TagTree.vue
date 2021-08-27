<template>
  <Tree :items="tags" #node="tag" childKey="children" class="TagTree">
    <li class="TagTree__list-item">
      <span class="Library__sidebar-row">
        <router-link :class="getFilterClass(tag.category, tag.taxonomy)"
                     :to="getFilterLink(tag.category, tag.taxonomy)">{{ tag.name }}</router-link>
      </span>
      <component :is="tag.children" />
    </li>
  </Tree>
</template>

<style>
.TagTree {
  margin: 0;
  padding: 0;
}

.TagTree__link {
  text-transform: uppercase;
}

.TagTree .TagTree .TagTree__link {
  text-transform: none;
}

</style>


<script>
import Tree from '../tree.js';

export default {
  name: 'TagTree',
  props: ['tags'],
  components: { Tree },
  methods: {
    getFilterLink(category, tag) {
      const query = Object.assign({}, this.$route.query);

      const values = new Set([].concat(query[category] || []));

      if (values.has(tag)) {
        values.delete(tag);
      } else {
        values.add(tag);
      }

      query[category] = Array.from(values);

      return { query };
    },
    getFilterClass(category, tag) {
      const current = this.$route.query[category];
      const categories = new Set(Array.isArray(current) ? current : [current]);
      return {
        'Library__filter-active': categories.has(tag),
        'TagTree__link': true
      };
    }
  }
};
</script>
