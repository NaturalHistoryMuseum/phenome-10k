<template>
  <div class="Library Subgrid" style="display: contents">
    <div class="Library__sort">
      Sort by:
      <ul class="Library__sort-list">
        <li :class="getSortLinkClass('name')"><router-link :to="getSortLink('name')">Name</router-link></li>
        <li :class="getSortLinkClass('geologic_age')"><router-link :to="getSortLink('geologic_age')">Geologic Age</router-link></li>
        <li :class="getSortLinkClass('ontogenic_age')"><router-link :to="getSortLink('ontogenic_age')">Ontogenic Age</router-link></li>
      </ul>
    </div>
    <div class="Content-Sidebar">
      <h3 class="Library__filter-header">Filter by:</h3>

      <SideSection title="Geologic Age">
        <TagTree :tags="tags.geologic_age"  class="Content-Sidebar__subgrid" />
      </SideSection>

      <SideSection title="Ontogenic Age">
        <TagTree :tags="tags.ontogenic_age" class="Content-Sidebar__subgrid" />
      </SideSection>

      <SideSection title="Taxonomy">
        <Tree :items="tags.taxonomy" #node="taxonomy" childKey="children" class="Content-Sidebar__subgrid" >
          <li :class="getTaxonFilterClass(taxonomy.id)" class="Content-Sidebar__subgrid" >
            <router-link :to="getTaxonFilterLink(taxonomy.id)">{{ taxonomy.name }}</router-link>
          </li>
        </Tree>
      </SideSection>
    </div>
    <div v-if="groups">
      <Group v-for="group in populatedGroups" :key="group.name" :name="group.group" :items="group.items" />
    </div>
    <Results v-else :results="results" />
  </div>
</template>

<script>
import Tree from '../tree.js';
import Results from './Results'
import TagTree from './TagTree'
import SideSection from './SideSection'

const Group = {
  name: 'Group',
  props: ['name', 'items'],
  render(h) {
    return h('div', [
      this.name,
      h(Results, { props: { results: this.items } })
    ]);
  }
}

export default {
  name: 'Library',
  components: {
    Group,
    Results,
    TagTree,
    Tree,
    SideSection
  },
  computed: {
    data() {
      return this.$route.meta.data;
    },
    groups(){
      return this.data.groups;
    },
    results(){
      return this.data.scans;
    },
    tags(){
      return this.data.tags;
    },
    populatedGroups(){
      return this.groups.filter(group => group.items.length)
    }
  },
  data(){
    return {
      menu: {
        geologicAge: false
      }
    }
  },
  methods: {
    getSortLink(sort) {
      const query = Object.assign({}, this.$route.query);
      query.sort = sort;
      return {
        query
      }
    },
    getSortLinkClass(field) {
      const cls = 'Library__sort-item';

      const o = {
        [cls]: true,
        [`${cls}--active`]: this.$route.query.sort === field
      }

      return o;
    },
    getTaxonFilterLink(tag) {
      const query = Object.assign({}, this.$route.query);

      const values = new Set([].concat(query.taxonomy))

      if(values.has(tag)) {
        values.delete(tag);
      }else{
        values.add(tag);
      }

      query.taxonomy = Array.from(values);

      return { query };
    },
    getTaxonFilterClass(tag) {
      const current = this.$route.query.taxonomy;
      const categories = new Set(Array.isArray(current) ? current : [current]);
      return categories.has(tag) && 'Library__filter-active';
    }
  }
}
</script>

<style>
.Library {

}

.Library__sort {
  text-transform: uppercase;
  margin-left: auto;
  font-family: 'HelveticaNeueW01-55Roma', Arial, Helvetica, sans-serif;
  color: #666;
  font-size: 11px;
}

.Library__sort-list{
  display: inline-flex;
  list-style: none;
  padding: 0;
}

.Library__sort-item {
  padding: 0 20px;
  font-weight: bold;
  color: #999;
}

.Library__sort-item:last-child {
  padding-right: 0;
}

.Library__sort-item:nth-child(n+2) {
  border-left: 1px solid;
}

.Library__sort-item a {
  color: inherit;
}

.Library__sort-item--active a {
  color: #096;
}

.Library__filter-active {
  font-weight: bold;
}

.Library__filter-header {
  font-weight: normal;
  font-size: inherit;
  padding: 0;
  margin: 0 0 10px 0;
}

.Library__sidebar-transition-enter-active,
.Library__sidebar-transition-leave-active {
  transition: height 1s ease-in-out;
  overflow: hidden;
}

.Library__sidebar-transition-enter,
.Library__sidebar-transition-leave-to {
  height: 0;
}

</style>
