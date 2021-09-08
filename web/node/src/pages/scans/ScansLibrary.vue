<template>
  <div :class="$style.main">
    <h1 class="Body__title">Scans</h1>

    <div class="Body__sidesection">
      <div :class="$style.sidebarRow">
        <h3 :class="$style.filterHeader">Filter by:</h3>
        <router-link v-if="showClearLink" :to="clearLink" :class="$style.sidebarClear">Clear All</router-link>
      </div>

      <SideSection title="Geologic Age" :count="selectedTagCount('geologic_age')">
        <TagTree :tags="tags.geologic_age" />
      </SideSection>

      <SideSection title="Ontogenetic Age" :count="selectedTagCount('ontogenic_age')">
        <TagTree :tags="tags.ontogenic_age" />
      </SideSection>

      <SideSection title="Elements" :count="selectedTagCount('elements')">
        <TagTree :tags="tags.elements" />
      </SideSection>

      <SideSection title="Taxonomy" :count="selectedTagCount('taxonomy')" :childClass="$style.sidebarRow">
        <Tree :items="tags.taxonomy" #node="taxonomy" childKey="children" :class="$style.taxonTree">
          <li :class="getTaxonFilterClass($style.taxon, taxonomy.id)">
            <router-link :class="getTaxonFilterClass($style.filter, taxonomy.id)"
                         :to="getTaxonFilterLink(taxonomy.id)">{{ taxonomy.name }}
            </router-link>
            <button v-if="taxonomy.hasChildren" :class="$style.taxExpand"
                    @click="$set(open, taxonomy.id, !open[taxonomy.id])">
              <img :src="'/static/' + (open[taxonomy.id] ? 'minus' : 'plus') + '.png'">
            </button>
            <component v-if="open[taxonomy.id]" :is="taxonomy.children" />
          </li>
        </Tree>
      </SideSection>
    </div>
    <div :class="[$style.filterControls, 'Body__filters']">
        <Search :class="$style.search" name="q" v-model="q" />
        <div :class="$style.sort" v-if="data.showMine">
          Viewing:
          <ul :class="$style.sortList">
            <li :class="getMineLinkClass(false)">
              <router-link :to="getMineLink(false)">All</router-link>
            </li>
            <li :class="getMineLinkClass(true)">
              <router-link :to="getMineLink(true)">Mine</router-link>
            </li>
          </ul>
        </div>
      </div>
    <div class="Body__content">
      <div v-if="groups">
        <Group v-for="group in populatedGroups" :key="group.name" :name="group.group" :items="group.items" />
      </div>
      <Results v-else :results="results" />
      <Pagination :page="page"
                  :total="totalPages"
                  :to="page => ({
                name: 'scans_library-paged',
                params: { page },
                query: this.$route.query
              })" />
    </div>
  </div>
</template>

<script>
import Tree from './components/tree.js';
import Results from './components/Results';
import TagTree from './components/TagTree';
import SideSection from './components/SideSection';
import SlideOpen from './components/SlideOpen.vue';
import Group from './components/group';
import Library from '../common/base/Library';


export default {
  name: 'ScansLibrary',
  extends: Library,
  components: {
    Group,
    Results,
    TagTree,
    Tree,
    SideSection,
    SlideOpen
  },
  data() {
    return {
      open: {},
      menu: {
        geologicAge: false
      }
    };
  },
  computed: {
    groups() {
      return this.data.groups;
    },
    results() {
      return this.data.scans;
    },
    tags() {
      return this.data.tags;
    },
    populatedGroups() {
      return this.groups.filter(group => group.items.length);
    },
    showClearLink() {
      return ['geologic_age', 'ontogenic_age', 'elements', 'taxonomy'].some(this.selectedTagCount);
    },
    clearLink() {
      const query = Object.assign({}, this.$route.query);
      query.geologic_age = query.ontogenic_age = query.elements = query.taxonomy = [];
      return {
        query
      };
    }
  },
  methods: {
    selectedTagCount(tag) {
      const t = this.$route.query[tag];
      return t ? (Array.isArray(t) ? t.length : 1) : 0;
    },
    getTaxonFilterLink(tag) {
      const query = Object.assign({}, this.$route.query);

      const values = new Set([].concat(query.taxonomy || []).map(str => parseInt(str, 10)));

      if (values.has(tag)) {
        values.delete(tag);
      } else {
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
        [`${ cls }--active`]: categories.has(tag)
      };
    }
  },
  mounted() {
    console.log(this.data);
  }
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

@import 'styles/common';
@import '../common/styles/sort';

.main {
  display: contents;
}

.taxExpand {
  appearance: none;
  background: transparent;
  border: none;
  padding: 0;
  line-height: 0;
  margin-bottom: -2px;

  &:hover {
    outline: 1px solid $palette-primary;
    cursor: copy;
  }
}

.taxon {
  background-image: linear-gradient(to left, transparent 0px, $palette-grey-5 1px, transparent 1px),
  linear-gradient(to bottom, transparent 6px, $palette-grey-5 7px, transparent 7px);
  background-repeat: no-repeat;
  background-size: 7px auto, 7px auto, auto;
  background-position-x: right;
  padding-right: 9px;
  list-style: none;
  text-align: right;
  display: grid;
  grid-template-columns: auto 12px;
  grid-template-areas: 'filter expand'
                       'tree   tree  ';
  grid-gap: 5px;
  justify-items: end;
  align-items: center;


  &:last-child {
    background-size: 7px 6px, 7px auto, auto;
  }

  & ul {
    padding-right: 4px;
    grid-area: tree;
  }

  & .filter {
    grid-area: filter;
    padding: 1px 5px 0;
  }

  & .taxExpand {
    grid-area: expand;
  }

  &--active {
    $bg: change-color($palette-primary, $alpha:0.2);

    background-image: linear-gradient(to left, transparent 0px, $palette-grey-5 1px, transparent 1px),
    linear-gradient(to bottom, transparent 6px, $palette-grey-5 7px, transparent 7px),
    linear-gradient(to bottom, $bg, $bg 100%, transparent 100%);
  }
}

.taxonTree {

}

.filterHeader {
  text-transform: uppercase;
  font-weight: normal;
  font-size: inherit;
  padding: 0;
  margin: 0;
}

.sidebarClear {
  grid-column-start: 3;
  text-transform: uppercase;
  color: $palette-primary;
}

.sidebarRow > *:first-child {
  margin-top: 0;
}
</style>
