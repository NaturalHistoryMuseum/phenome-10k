<template>
  <Scan v-if="type=='scan'" v-bind="$attrs" />
  <Publication v-else  v-bind="$attrs" />
</template>

<script>
/**
 * ScanOrPublication component - because both of these page types use the same path,
 * we need a middle component to display a different view depending on the data we get
 * back from the server.
 */
export default {
  components: {
    Scan: () => import('./Scan'),
    Publication: { render: h => h('div', ['Publication']) }
  },
  computed: {
    type() {
      return this.$route.meta.data.type;
    }
  }
}
</script>
