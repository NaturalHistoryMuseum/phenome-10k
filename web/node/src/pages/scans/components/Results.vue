<template>
  <ul :class="$style.main">
    <li v-for="scan in results" :key="scan.url_slug">
      <router-link :to="scan.url_slug" :class="$style.link">
        <!--        <img :src="scan.thumbnail + '?w=155'" alt="" />-->
        <img src="http://placekitten.com/155/116" alt="" />
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
  grid-template-columns: repeat(auto-fill, minmax(160px,auto));
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
}

.title {
  padding: 15px 10px;
  color: black;
  line-height: 1.2em;
}
</style>
