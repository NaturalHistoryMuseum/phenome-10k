<template>
    <div class="Upload3D" @dragover="dragOver" @dragleave="dragEnd" @drop="drop">
        <label :class="labelClass" v-show="progress == null">
            <div class="Upload3D__drop-text">Drop scan here</div>
            <div class="Upload3D__or">or</div>
            <div class="Upload3D__select">Select File</div>
            <input type="file" name="file" @change="fileChange" class="Upload3D__file" />
        </label>
        <div v-if="progress != null" class="Upload3D__progress">
            <progress class="Upload3D__progress-bar" :value="progress" max="100"></progress>
            <div class="Upload3D__progress-text">{{ progress }}%</div>
        </div>
        <Errors :errors="errors" />
      </div>
</template>

<script>
import Errors from '../forms/Errors';

export default  {
    name: 'Upload3D',
    components: {
      Errors
    },
    props:['progress', 'errors'],
    data(){
        return {
            dragging: false
        }
    },
    computed: {
        labelClass(){
            const cls = ['Upload3D__input'];
            if(this.dragging) {
                cls.push('Upload3D__input--hovered')
            }
            return cls.join(' ');
        }
    },
    methods: {
        fileChange(e) {
            this.uploadFile(e.target.form);
        },
        dragOver(e){
            e.preventDefault();
            this.dragging = true;
        },
        dragEnd(e){
            e.preventDefault();
            this.dragging = false;
        },
        drop(e){
            e.preventDefault();
            const input = e.target.control;
            input.files = e.dataTransfer.files;
            this.uploadFile(e.target.form);
        },
        uploadFile(form){
            if(!form) {
                this.dragging = false;
                return;
            }
            this.$emit('change', form)
        }
    }
}
</script>

<style>
.Upload3D {
    width: 100%;
    height: 900px;
}

.Upload3D__input {
    height: 100%;
    background: #f2f2f2;
    display: grid;
    align-content: center;
    justify-items: center;
}

.Upload3D__input--hovered {
    background: #ccc;
    border: 3px dashed #666;
}

.Upload3D__drop-text {
    color: #096;
    font-family: 'Neo Sans W01', Arial, Helvetica, sans-serif;
    font-size: 24px;
    text-transform: uppercase;
    line-height: 20px;
}

.Upload3D__select {
    display: block;
    width: 110px;
    background: #ebebeb;
    font-size: 13px;
    color: #333;
    font-family: 'HelveticaNeueW01-55Roma', Arial, Helvetica, sans-serif;
    margin: 0 auto;
    padding: 5px 0;
    border: 1px solid #666;
    text-align: center;
}

.Upload3D__file {
    width: 0px;
}

.Upload3D__or {
    font-size: 12px;
    font-family: 'Supria Sans W01 Medium', Arial, Helvetica, sans-serif;
    color: #666;
    line-height: 9px;
    margin: 15px 0;
}

.Upload3D__progress {
    height: 100%;
    width: 100%;
    display: grid;
    align-content: stretch;
    justify-items: center;
    grid-template-areas: 'content';
}

.Upload3D__progress-bar {
    height: 100%;
    width: 100%;
    grid-area: content;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
}

.Upload3D__progress-bar::-webkit-progress-value,
.Upload3D__progress-bar::-moz-progress-bar {
    background: #096;
}

.Upload3D__progress-text {
    grid-area: content;
    line-height: 200px;
    font-size: 100px;
    color: #333;
    font-family: 'Neo Sans W01 Medium', Arial, Helvetica, sans-serif;
    align-self: center;
}
</style>
