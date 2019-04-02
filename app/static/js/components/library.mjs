export default {
  name: 'Library',
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
    }
  },
  template:`<div class="Library">
    <div>
      Sort by:
      <ul>
        <li><router-link :to="{ query: { sort: 'name' }}">Name</router-link></li>
        <li>Geologic Age</li>
        <li>Ontogenic Age</li>
      </ul>
    </div>
    <ul class="Library__results">
      <li v-for="scan in results">
        <a :href="scan.url_slug" class="Library__result">
          <img :src="scan.thumbnail" alt="" class="Library__thumb" />
          <span class="Library__title">{{ scan.scientific_name }}</span>
        </a>
      </li>
    </ul>
  </div>`
}
