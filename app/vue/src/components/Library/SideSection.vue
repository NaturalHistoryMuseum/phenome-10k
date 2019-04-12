<template>
  <div class="Content-Sidebar__subgrid">
    <button @click="open = !open" style="appearance: none; font: inherit; background: transparent; border: none;">
      {{ title }}
    </button>
    <img :src="'/static/' + (open ? 'minus' : 'plus') + '.png'" style="grid-column-start: 2">
    <transition name="Library__sidebar-transition" @enter="enter" @afterEnter="afterEnter" @leave="leave">
      <div v-show="open" class="Content-Sidebar__subgrid">
        <slot />
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'SideSection',
  props: ['title'],
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
