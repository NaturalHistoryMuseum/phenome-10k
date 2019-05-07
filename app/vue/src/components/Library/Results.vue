<template>
  <ul class="Results">
    <li v-for="scan in results" :key="scan.url_slug">
      <router-link :to="scan.url_slug" class="Results__link">
        <img :src="scan.thumbnail + '?w=155'" alt="" />
        <span class="Results__title">{{ scan.scientific_name }}</span>
      </router-link>
    </li>
  </ul>
</template>

<style>
.Results {
  display: flex;
  flex-wrap: wrap;
  margin: 0;
  padding: 0;
  list-style: none;
}

.Results > * {
  margin: 0;
  padding: 0;
}

.Results__link {
  display: flex;
  flex-direction: column;
  margin: 7.5px 2.5px;
}

.Results__title {
  padding: 15px 10px;
  color: black;
}
</style>

<script>
export default {
  name: 'Results',
  props: ['results']
}
</script>
