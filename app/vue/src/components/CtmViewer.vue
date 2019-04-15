<template>
  <canvas class="CtmViewer" ref="canvas" :height="height" :width="width" @dblclick="toggelFullscreen"></canvas>
</template>

<style>
.CtmViewer {
  width: 100%;
  max-width: 100%;
}
</style>

<script>
import JSC3D from "jsc3d/jsc3d/jsc3d.js"
import "jsc3d/jsc3d/jsc3d.ctm.js"
import "jsc3d/jsc3d/jsc3d.webgl.js"
import "jsc3d/jsc3d/jsc3d.touch.js"
import ResizeObserver from 'resize-observer-polyfill';

export default {
    name: 'ctm',
    props: {
      src: String,
      width: {
        type: [String, Number],
        default: 720
      },
      height: {
        type: [String, Number],
        default: 500
      },
    },
    $viewer: null,
    mounted(){
      const viewer = new JSC3D.Viewer(this.$refs.canvas);
      viewer.setParameter('SceneUrl', this.src);
      viewer.setParameter('RenderMode', 'smooth');
      viewer.setParameter('Renderer', 'webgl');
      viewer.setParameter('ModelColor', '#666666');
      viewer.setParameter('Definition', 'high');
      viewer.setParameter('ProgressBar', 'on');
      viewer.setParameter('BackgroundColor1', '#09090a');
      viewer.setParameter('BackgroundColor2', '#676767');
      viewer.init();
      viewer.update();

      // Resize the viewer when the canvas size changes
      this.ro = new ResizeObserver((entries, observer) => {
        const ratio = this.width / this.height;

        // Only care about the most recent entry
        const { width, height } = entries.pop().contentRect;

        // Set the canvas's JS dimensions, as the css may override them,
        // causing the contentRect to be different to the apparent canvas dimensions
        this.$refs.canvas.width = width;

        // If we're in full screen, use the full height of the content rect,
        // otherwise just use the ratio given by the props
        this.$refs.canvas.height = document.fullscreenElement ? height : width / ratio;

        // Re-initialise the viewer to take into account the new size
        viewer.init();
      });
      this.ro.observe(this.$refs.canvas)
    },
    beforeDestroy(){
      this.ro.disconnect();
    },
    methods: {
      /**
       * Utility method to allow other components to get the current rendered frame
       * as an image file.
       * @param name The filename for the captured image
       */
      captureStill(name) {
          return new Promise(resolve =>
              this.$refs.canvas.toBlob(blob =>
              resolve(new File([blob], name))
              )
          );
      },
      /**
       * Enable or disable fullscreen
       */
      toggelFullscreen(){
        if(!document.fullscreenElement) {
          this.$refs.canvas.requestFullscreen()
        } else {
          document.exitFullscreen()
        }
      }
  }
}
</script>
