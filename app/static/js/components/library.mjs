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
      const cls = "Content-Sidebar__subgrid";

      const current = this.$route.query[category];
      const categories = new Set(Array.isArray(current) ? current : [current]);
      return categories.has(tag) ? ['Library__filter-active', cls] : cls;
    }
  },
  template: `<Tree :items="tags" #node="tag" childKey="children" class="Content-Sidebar__subgrid">
    <li :class="getFilterClass(tag.category, tag.taxonomy)">
      <router-link :to="getFilterLink(tag.category, tag.taxonomy)">{{ tag.name }}</router-link>
    </li>
  </Tree>`
}

const SideSection = {
  name: 'SideSection',
  props: ['title'],
  data() {
    return {
      open: false
    }
  },
  methods: {
    enter(element) {
      const width = getComputedStyle(element).width;

      element.style.width = width;
      element.style.position = 'absolute';
      element.style.visibility = 'hidden';
      element.style.height = 'auto';

      const height = getComputedStyle(element).height;

      element.style.width = null;
      element.style.position = null;
      element.style.visibility = null;
      element.style.height = 0;

      // Force repaint to make sure the
      // animation is triggered correctly.
      getComputedStyle(element).height;

      // Trigger the animation.
      // We use `setTimeout` because we need
      // to make sure the browser has finished
      // painting after setting the `height`
      // to `0` in the line above.
      setTimeout(() => {
        element.style.height = height;
      });
    },
    afterEnter(element) {
      element.style.height = 'auto';
    },
    leave(element) {
      const height = getComputedStyle(element).height;

      element.style.height = height;

      // Force repaint to make sure the
      // animation is triggered correctly.
      getComputedStyle(element).height;

      setTimeout(() => {
        element.style.height = 0;
      });
    }
  },
  template: `<div class="Content-Sidebar__subgrid">
    <button @click="open = !open" style="appearance: none; font: inherit; background: transparent; border: none;">
      {{ title }}
    </button>
    <img :src="'/static/' + (open ? 'minus' : 'plus') + '.png'" style="grid-column-start: 2">
    <transition name="Library__sidebar-transition" @enter="enter" @afterEnter="afterEnter" @leave="leave">
      <div v-show="open" class="Content-Sidebar__subgrid">
        <slot />
      </div>
    </transition>
  </div>`
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
  inject: ['defaultData'],
  css: ['/static/js/components/library.css'],
  data(){
    return {
      groups: this.defaultData.groups,
      results: this.defaultData.scans,
      tags: this.defaultData.tags,
      menu: {
        geologicAge: false
      }
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
      let cls = 'Library__sort-item';
      if(this.$route.query.sort === field) {
        cls += ` ${cls}--active`;
      }
      return cls;
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
  },
  template:`<div class="Library Subgrid" style="display: contents">
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
      <Group v-for="group in groups" v-if="group.items.length" :key="group.name" :name="group.group" :items="group.items" />
    </div>
    <Results v-else :results=results />
  </div>`
}

