<template>
  <transition name="SlideOpen__main-" @enter="enter" @afterEnter="afterEnter" @leave="leave">
    <slot />
  </transition>
</template>

<script>
export default {
  name: 'SlideOpen',
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
};
</script>

<style lang="scss">
// this is a slightly hacky way to get the required classes while using modules
.main {
  &--enter-active {
    transition: height 0.3s ease-out;
    overflow: hidden;
  }

  &--leave-active {
    transition: height 0.3s ease-out;
    overflow: hidden;
  }

  &--enter,
  &--leave-to {
    height: 0;
  }
}
</style>
