<template>
  <Tree :items="tags" #node="tag" childKey="children" :class="$style.main">
    <li :class="$style.listItem">
      <span :class="$style.sidebarRow">
        <router-link :class="getFilterClass(tag.category, tag.taxonomy)"
                     :to="getFilterLink(tag.category, tag.taxonomy)">{{ tag.name }}</router-link>
      </span>
      <component :is="tag.children"/>
    </li>
  </Tree>
</template>

<script>
import Tree from './tree.js';

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
      let classDict = {};
      classDict[this.$style.link] = true;
      classDict[this.$style['filter--active']] = categories.has(tag);
      return classDict;
    }
  }
};
</script>

<style module lang="scss">
@import '../styles/common';
@import 'scss/palette';

.main {
  margin: 0;
  padding: 0;

  & .link {
    text-transform: uppercase;
    margin-top: 5px;
  }

  & .main .link {
    text-transform: none;
    margin-top: 0;
  }
}

.listItem {

}
</style>
