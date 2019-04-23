<template>
  <div class="SideSection">
    <div class="Library__sidebar-row SideSection__title">
      <button @click="open = !open" class="SideSection__button">
        {{ title }}
      </button>
      <img :src="'/static/' + (open ? 'minus' : 'plus') + '.png'">
      <div v-if="count">
        ({{ count }})
      </div>
    </div>
    <SlideOpen>
      <div v-show="open" :class="childClass">
        <slot />
      </div>
    </SlideOpen>
  </div>
</template>

<style>
.SideSection__button {
  text-transform: uppercase;
  appearance: none;
  font: inherit;
  background: transparent;
  border: none;
  color: inherit;
}

.SideSection__title {
  color: #096;
}
</style>

<script>
import SlideOpen from './SlideOpen.vue';

export default {
  name: 'SideSection',
  props: ['title', 'count', 'childClass'],
  components: { SlideOpen },
  data() {
    return {
      open: false
    }
  },
  methods: {
    enter(element) {
      const width = getComputedStyle(element).width;

      element.style.width = width;
      element.style.position = 'absolute';
      element.style.visibility = 'hidden';
      element.style.height = 'auto';

      const height = getComputedStyle(element).height;

      element.style.width = null;
      element.style.position = null;
      element.style.visibility = null;
      element.style.height = 0;

      // Force repaint to make sure the
      // animation is triggered correctly.
      getComputedStyle(element).height;

      // Trigger the animation.
      // We use `setTimeout` because we need
      // to make sure the browser has finished
      // painting after setting the `height`
      // to `0` in the line above.
      setTimeout(() => {
        element.style.height = height;
      });
    },
    afterEnter(element) {
      element.style.height = 'auto';
    },
    leave(element) {
      const height = getComputedStyle(element).height;

      element.style.height = height;

      // Force repaint to make sure the
      // animation is triggered correctly.
      getComputedStyle(element).height;

      setTimeout(() => {
        element.style.height = 0;
      });
    }
  }
}
</script>
