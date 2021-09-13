<template>
  <ul :class="$style.main">
    <li v-for="scan in results" :key="scan.url_slug">
      <router-link :to="{name: 'scan_view', params: {id: scan.url_slug}}" :class="$style.link">
        <img :src="scan.thumbnail + '?w=155'" :alt="scan.url_slug" :class="$style.thumbnail"/>
        <span :class="$style.title">{{ scan.scientific_name }}</span>
      </router-link>
    </li>
  </ul>
</template>

<script>
export default {
  name: 'Results',
  props: ['results']
};
</script>

<style module lang="scss">
.main {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: minmax(100px, auto);
  grid-gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;

  & > * {
    margin: 0;
    padding: 0;
  }
}

.link {
  display: flex;
  flex-direction: column;
  margin: 7.5px 2.5px;
  align-items: center;
  justify-content: end;
  height: 100%;
}

.title {
  padding: 15px 0;
  color: black;
  line-height: 1.2em;
  text-align: center;
}

.thumbnail {
  font-size: 0.8em;
}
</style>
