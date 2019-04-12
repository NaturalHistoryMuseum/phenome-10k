<template>
  <ul class="Library__results">
    <li v-for="scan in results" :key="scan.url_slug"><a :href="scan.url_slug" class="Library__result">
      <img :src="scan.thumbnail" alt="" class="Library__thumb" />
     <span class="Library__title">{{ scan.scientific_name }}</span>
   </a></li>
  </ul>
</template>

<script>
export default {
  name: 'Results',
  props: ['results']
}
</script>
