import Tree from './tree.mjs';

const Results = {
  name: 'Results',
  props: ['results'],
  template: `
  <ul class="Library__results">
    <li v-for="scan in results"><a :href="scan.url_slug" class="Library__result">
      <img :src="scan.thumbnail" alt="" class="Library__thumb" />
     <span class="Library__title">{{ scan.scientific_name }}</span>
   </a></li>
  </ul>`
}

const Group = {
  name: 'Group',
  components: { Results },
  props: ['name', 'items'],
  template: `<div>{{ name }}<Results :results="items"/></div>`
}

const TagTree = {
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
      return categories.has(tag) && 'Library__filter-active';
    }
  },
  template: `<Tree :items="tags" #node="tag" childKey="children">
    <li :class="getFilterClass(tag.category, tag.taxonomy)">
      <router-link :to="getFilterLink(tag.category, tag.taxonomy)">{{ tag.name }}</router-link>
    </li>
  </Tree>`
}

export default {
  name: 'Library',
  components: {
    Group,
    Results,
    TagTree
  },
  inject: ['defaultData'],
  css: ['/static/js/components/library.css'],
  data(){
    return {
      groups: this.defaultData.groups,
      results: this.defaultData.scans,
      tags: this.defaultData.tags,
    }
  },
  watch: {
    '$route': 'fetchData'
  },
  methods: {
    async fetchData() {
      const res = await fetch(window.location, { headers: { accept: 'application/javascript' } });
      const data = await res.json();
      this.groups = data.groups;
      this.results = data.scans;
    },
    getSortLink(sort) {
      const query = Object.assign({}, this.$route.query);
      query.sort = sort;
      return {
        query
      }
    },
    getSortLinkClass(field) {
      return this.$route.query.sort === field ? 'Library__sort-active' : ''
    }
  },
  template:`<div class="Library Subgrid" style="display: contents">
    <div>
      Sort by:
      <ul>
        <li :class="getSortLinkClass('name')"><router-link :to="getSortLink('name')">Name</router-link></li>
        <li :class="getSortLinkClass('geologic_age')"><router-link :to="getSortLink('geologic_age')">Geologic Age</router-link></li>
        <li :class="getSortLinkClass('ontogenic_age')"><router-link :to="getSortLink('ontogenic_age')">Ontogenic Age</router-link></li>
      </ul>
    </div>
    <div style="grid-column-start:1">
      <h3>Filter</h3>
      <h4>Geologic Age:</h4>
      <TagTree :tags="tags.geologic_age" />

      <h4>Ontogenic Age:</h4>
      <TagTree :tags="tags.ontogenic_age" />
    </div>
    <div v-if="groups">
      <Group v-for="group in groups" v-if="group.items.length" :key="group.name" :name="group.group" :items="group.items" />
    </div>
    <Results v-else :results=results />
  </div>`
}

