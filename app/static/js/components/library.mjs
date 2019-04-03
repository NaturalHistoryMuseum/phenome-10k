
const Results = {
  name: 'Results',
  props: ['results'],
  template: `
  <ul v-else class="Library__results">
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

export default {
  name: 'Library',
  components: {
    Group,
    Results
  },
  inject: ['defaultData'],
  css: ['/static/js/components/library.css'],
  data(){
    return {
      results: this.defaultData
    }
  },
  watch: {
    '$route': 'fetchData'
  },
  methods: {
    async fetchData() {
      const res = await fetch(window.location, { headers: { accept: 'application/javascript' } });
      const data = await res.json();
      this.results = data;
    },
    getSortLink(sort) {
      return {
        query: { sort }
      }
    },
    getSortLinkClass(field) {
      return this.$route.query.sort === field ? 'Library__sort-active' : ''
    }
  },
  template:`<div class="Library">
    <div>
      Sort by:
      <ul>
        <li :class="getSortLinkClass('name')"><router-link :to="getSortLink('name')">Name</router-link></li>
        <li :class="getSortLinkClass('geologic_age')"><router-link :to="getSortLink('geologic_age')">Geologic Age</router-link></li>
        <li>Ontogenic Age</li>
      </ul>
    </div>
    <div v-if="results.groups">
      <Group v-for="group in results.groups" v-if="group.items.length" key="group.name" :name="group.group" :items="group.items" />
    </div>
    <Results v-else :results=results />
  </div>`
}

