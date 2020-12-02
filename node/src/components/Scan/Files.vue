<template>
  <div class="Files">
    <h3 class="Files-subheader">{{ title }}</h3>
    <a :href="download" class="Files-download">Download <img src="/static/download.png" alt=""></a>
    <div class="Files-list">
      <slot />
    </div>
  </div>
</template>

<style>
.Files {
  display: flex;
  flex-wrap: wrap;
  margin-top: 20px;
}

.Files-subheader {
  text-transform: uppercase;
  font-size: 12px;
  font-weight: normal;
  margin: 0;
}

.Files-download {
  color: #7f7f7f;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  margin-left: auto;
}

.Files-list {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  margin: 10px 0;

}
</style>

<script>
export default {
  props: ['title', 'download']
}
</script>
