<template>
  <ul class="Errors">
    <li v-for="error in errors" :key="error">
      {{ error.message || error }}
    </li>
  </ul>
</template>

<style>
.Errors {
  list-style: none;
  margin: 0;
  padding: 0;
}

.Errors li {
  color: red;
}
</style>

<script>
export default {
  name: 'FormErrors',
  props: ['errors']
}
</script>
