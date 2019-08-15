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
import CTM from 'jsc3d/ctm-loader';
import { Viewer, registerLoader } from "jsc3d/index.js";

registerLoader(CTM);

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
      this.$nextTick(() => {
        const viewer = new Viewer(this.$refs.canvas);
        viewer.setParameter('SceneUrl', this.src);
        viewer.setParameter('RenderMode', 'smooth');
        viewer.setParameter('Renderer', 'webgl');
        viewer.setParameter('ModelColor', '#666666');
        viewer.setParameter('Definition', 'high');
        viewer.setParameter('ProgressBar', 'on');
        viewer.setParameter('BackgroundColor1', '#09090a');
        viewer.setParameter('BackgroundColor2', '#676767');

        this.viewer = viewer;

        this.resize(true);

        this.resizeLisener = () => this.resize();

        window.addEventListener('resize', this.resizeLisener);
      });
    },
    beforeDestroy(){
      window.removeEventListener('resize', this.resizeLisener);
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
      async toggelFullscreen(){
        if(!document.fullscreenElement) {
          await this.$refs.canvas.requestFullscreen()
        } else {
          await document.exitFullscreen()
        }
        this.resize();
      },

      resize(force = false){
        const canvas = this.$refs.canvas;

        // Resize the viewer when the canvas size changes
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;

        if(!force && (width === canvas.width)) {
          return;
        }

        const ratio = parseInt(this.width, 10) / parseInt(this.height, 10);

        // Set the canvas's JS dimensions, as the css may override them,
        // causing the contentRect to be different to the apparent canvas dimensions
        canvas.width = width;

        // If we're in full screen, use the full height of the content rect,
        // otherwise just use the ratio given by the props
        canvas.height = document.fullscreenElement ? height : (width / ratio);

        // Stop re-init creating new webGL instance (reuse the old one)
        if(this.viewer.webglBackend) {
          this.viewer.useWebGL = false;
        }

        // Re-initialise the viewer to take into account the new size
        this.viewer.init();
      }
  }
}
</script>
