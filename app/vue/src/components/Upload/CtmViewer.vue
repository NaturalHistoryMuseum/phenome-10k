<template>
  <canvas ref="canvas" :height="height" :width="width" ></canvas>
</template>

<script>
import JSC3D from "./jsc3d/jsc3d.js"
import "./jsc3d/jsc3d.ctm.js"
import "./jsc3d/jsc3d.webgl.js"
import "./jsc3d/jsc3d.touch.js"

export default {
    name: 'ctm',
    props: ['src', 'height', 'width'],
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
    },
    methods: {
        captureStill(name) {
            return new Promise(resolve =>
                this.$refs.canvas.toBlob(blob =>
                resolve(new File([blob], name))
                )
            );
        }
    }
}
</script>
