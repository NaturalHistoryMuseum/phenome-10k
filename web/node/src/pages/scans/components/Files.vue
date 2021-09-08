<template>
  <div :class="$style.main">
    <div :class="$style.header">
      <h3 :class="$style.subheader">{{ title }}</h3>
      <a :href="download" :class="$style.downloadLink">
        <span>Download</span>
        <img src="/static/download.png" alt="">
      </a>
    </div>
    <div :class="$style.list">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  props: ['title', 'download']
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

.main {
  margin-top: 20px;
}

.header {
  display: flex;
  text-transform: uppercase;
}

.subheader {
  margin: 0;
  font-size: $body-font-size;
}

.downloadLink {
  color: $palette-grey-2;
  margin-left: auto;
  font-size: $small-font-size;

  & span {
    margin-right: 2px;
  }

  & img {
    margin-bottom: -1px;
  }
}

.list {
  width: 100%;
  margin: 10px 0;

}
</style>
