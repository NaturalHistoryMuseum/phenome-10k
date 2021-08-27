<template>
  <div class="Library">
    <div class="Body__sidesection">
      <div class="Library__sidebar-row">
        <h3 class="Library__filter-header">Filter by:</h3>
        <router-link v-if="showClearLink" :to="clearLink" class="Library__sidebar-clear">Clear All</router-link>
      </div>

      <SideSection title="Geologic Age" :count="selectedTagCount('geologic_age')">
        <TagTree :tags="tags.geologic_age" />
      </SideSection>

      <SideSection title="Ontogenetic Age" :count="selectedTagCount('ontogenic_age')">
        <TagTree :tags="tags.ontogenic_age"/>
      </SideSection>

      <SideSection title="Elements" :count="selectedTagCount('elements')">
        <TagTree :tags="tags.elements"/>
      </SideSection>

      <SideSection title="Taxonomy" :count="selectedTagCount('taxonomy')" childClass="Library__sidebar-row">
        <Tree :items="tags.taxonomy" #node="taxonomy" childKey="children" class="Library__taxon-tree">
          <li :class="getTaxonFilterClass('Library__taxon', taxonomy.id)">
            <button v-if="taxonomy.hasChildren" class="Library__tax-expand" @click="$set(open, taxonomy.id, !open[taxonomy.id])">
              <img :src="'/static/' + (open[taxonomy.id] ? 'minus' : 'plus') + '.png'">
            </button>
            <router-link :class="getTaxonFilterClass('Library__filter', taxonomy.id)" :to="getTaxonFilterLink(taxonomy.id)">{{ taxonomy.name }}</router-link>
            <!--SlideOpen :key="taxonomy.id"-->
              <component v-if="open[taxonomy.id]" :is="taxonomy.children" />
            <!--/SlideOpen-->
          </li>
        </Tree>
      </SideSection>
    </div>
    <div class="Body__content">
      <div class="Library__filter-controls">
      <Search class="Library__search" name="q" v-model="q" />
      <div class="Library__sort" v-if="data.showMine">
        Viewing:
        <ul class="Library__sort-list">
          <li :class="getMineLinkClass(false)"><router-link :to="getMineLink(false)">All</router-link></li>
          <li :class="getMineLinkClass(true)"><router-link :to="getMineLink(true)">Mine</router-link></li>
        </ul>
      </div>
    </div>

    <div v-if="groups">
      <Group v-for="group in populatedGroups" :key="group.name" :name="group.group" :items="group.items" />
    </div>
    <Results v-else :results="results" />
    <Pagination :page="data.page"
            :total="data.total_pages"
            :to="page => ({
                name: 'library-paged',
                params: { page },
                query: this.$route.query
              })"
            class="Publications__footer" />
    </div>
  </div>
</template>

<script>
import Tree from '../tree.js';
import Results from './Results'
import TagTree from './TagTree'
import SideSection from './SideSection'
import SlideOpen from './SlideOpen.vue';
import Search from '../forms/Search';
import Pagination from '../Pagination';

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
    SideSection,
    SlideOpen,
    Search,
    Pagination
  },
  data(){
    return {
      open: {},
      menu: {
        geologicAge: false
      },
      q: this.$route.meta.data.q
    }
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
    },
    showClearLink() {
      return ['geologic_age', 'ontogenic_age', 'elements', 'taxonomy'].some(this.selectedTagCount);
    },
    clearLink() {
      const query = Object.assign({}, this.$route.query);
      query.geologic_age = query.ontogenic_age = query.elements = query.taxonomy = [];
      return {
        query
      }
    }
  },
  methods: {
    /**
     * Get the router-link `to` param for "View Mine"/"View All" links
     * @param {boolean} mine true = view mine, false = view all
     */
    getMineLink(mine) {
      const query = Object.assign({}, this.$route.query);
      // We only care about the presence of the `mine` parameter, not its value
      if(mine) {
        query.mine = null;
      } else {
        delete query.mine;
      }

      return {
        query
      }
    },
    /**
     * Get the css class for the "View Mine"/"View All" links
     * @param {bool} mine true=view mine, false = view all
     */
    getMineLinkClass(mine) {
      const cls = 'Library__sort-item';

      return {
        [cls]: true,
        [`${cls}--active`]: mine === ('mine' in this.$route.query)
      }
    },
    getSortLink(sort) {
      const query = Object.assign({}, this.$route.query);
      query.sort = sort;
      return {
        query
      }
    },
    selectedTagCount(tag){
      const t = this.$route.query[tag];
      return t ? (Array.isArray(t) ? t.length : 1) : 0;
    },
    getSortLinkClass(field) {
      const cls = 'Library__sort-item';

      return {
        [cls]: true,
        [`${cls}--active`]: (this.$route.query.sort || 'name') === field
      }
    },
    getTaxonFilterLink(tag) {
      const query = Object.assign({}, this.$route.query);

      const values = new Set([].concat(query.taxonomy || []).map(str => parseInt(str, 10)))

      if(values.has(tag)) {
        values.delete(tag);
      }else{
        values.add(tag);
      }

      query.taxonomy = Array.from(values);

      return { query };
    },
    getTaxonFilterClass(cls, tag) {
      const current = this.$route.query.taxonomy || [];
      const categories = new Set([].concat(current).map(str => parseInt(str, 10)));
      return {
        [cls]: true,
        [`${cls}--active`]: categories.has(tag)
      };
    }
  }
}
</script>

<style>
.Library {
  display: contents;
}

.Library__tax-expand {
  appearance: none;
  background: transparent;
  border: none;
  padding: 0;
  line-height: 6px;
  margin: 1px -2px 0;
}

.Library__tax-expand:hover {
  outline: 1px solid #096;
  cursor: copy;
}

.Library__taxon {
  background-image: linear-gradient(to right, transparent 0px, gray 1px, transparent 1px),
                    linear-gradient(to bottom, transparent 6px, gray 7px, transparent 7px);
  background-repeat: no-repeat;
  background-size: 7px auto, 7px auto, auto;
  padding-left: 9px;
  list-style: none;
}

.Library__taxon--active {
    background-image:
      linear-gradient(to right, transparent 0px, gray 1px, transparent 1px),
      linear-gradient(to bottom, transparent 6px, gray 7px, transparent 7px),
      linear-gradient(to bottom, #0963, #0963 15px, transparent 15px);
}

.Library__taxon:last-child {
  background-size: 7px 6px, 7px auto, auto;
}

.Library__taxon ul {
  padding-left: 4px;
}

.Library__sort {
  text-transform: uppercase;
  margin-left: auto;
  font-family: 'HelveticaNeueW01-55Roma', Arial, Helvetica, sans-serif;
  color: #666;
  font-size: 11px;
  grid-column-start: 2;
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

.Library__filter--active {
  font-weight: bold;
}

.Library__filter:hover {
  background: #0963;
}

.Library__filter-header {
  text-transform: uppercase;
  font-weight: normal;
  font-size: inherit;
  padding: 0;
  margin: 0 0 10px 0;
}

.Library__sidebar-row {
   display: grid;
   grid-template-columns: 222px 20px auto;
   margin: 5px 0;
}

.Library__sidebar-row :first-child {
  justify-self: end;
}

.Library__sidebar-clear {
  grid-column-start: 3;
  text-transform: uppercase;
  color: #096;

}

.Library__filter-controls {
  display: grid;
  grid-template-columns: auto auto;
}

.Library__search {
  justify-self: start;
  align-self: start;
}
</style>
