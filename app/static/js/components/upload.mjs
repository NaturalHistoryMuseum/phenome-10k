const xhrUpload = (form, progress) => {
    const formData = new FormData(form);
    const xhr = new XMLHttpRequest()
    xhr.open('POST', form.action)
    xhr.setRequestHeader('Accept', 'application/json')
    const ready = new Promise((res, rej) => {
        xhr.onload = () => res(xhr);
        xhr.onerror = rej
    });

    xhr.upload.onprogress = function (event) {
        if (event.lengthComputable) {
            progress(Math.round((event.loaded / event.total) * 100))
        }
    }

    xhr.send(formData);

    return ready;
}

const CtmViewer = {
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
    template: `
        <div>
        <canvas ref="canvas" :height="height" :width="width" ></canvas>
        </div>
    `,
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

const Upload3D = {
    name: 'upload',
    template: `
    <div class="Upload3D" @dragover="dragOver" @dragleave="dragEnd" @drop="drop">
        <label :class="labelClass" v-show="!uploading">
            <div class="Upload3D__drop-text">Drop STL here</div>
            <div class="Upload3D__or">or</div>
            <div class="Upload3D__select">Select File</div>
            <input type="file" name="file" @change="fileChange" class="Upload3D__file" />
        </label>
        <div v-if="uploading" class="Upload3D__progress">
            <progress class="Upload3D__progress-bar" :value="progress" max="100"></progress>
            <div class="Upload3D__progress-text">{{ progress }}%</div>
        </div>
      </div>
    `,
    props:['progress'],
    data(){
        return {
            dragging: false,
            uploading: false
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
                this.uploading = false;
                this.dragging = false;
                return;
            }
            this.uploading = true;
            this.$emit('change', form)
        }
    }
}

export default {
    async mounted(){
        const id = this.$route.params.id;
        if(id) {
            const res = await fetch(`/${id}/edit`, {
                headers: { accept: 'application/javascript' }
            });
            const { scan, form } = await res.json();

            this.scan = scan;
            this.form = form;
        }
    },
    name: 'Upload',
scripts: ["/static/js/jsc3d/jsc3d.js",
    "/static/js/jsc3d/jsc3d.ctm.js",
    "/static/js/jsc3d/jsc3d.webgl.js",
    "/static/js/jsc3d/jsc3d.touch.js"],
  props: [
    "error",
  ],
  inject: ['defaultData'],
  data() {
      return {
          scan: null,
          progress: null,
          stills: [],
          pubList: [],
          csrf: this.defaultData.csrf_token,
          form: this.defaultData.form
        };
  },
  computed: {
      stillUrls() {
          return [
              ...this.scan.attachments.map(a => '/' + a),
              ...this.stills.map(file => URL.createObjectURL(file))
          ]
      },
      formAction(){
        return this.scan ? `/${this.scan.id}/edit` : '';
      },
      savedPublications() {
        const scanPubs = this.scan ? this.scan.publications : [];
        const formPubIds = this.form.publications.data || [];
        const pubsList = [...scanPubs, ...this.pubList];
        return formPubIds.map(id => pubsList.find(pub => pub.id === id) || { id, title: id });
      }
  },
  methods: {
    async submit({ target }){
        const data = new FormData(target);
        const res =  await fetch(target.action, {
            method: 'POST',
            headers: { accept: 'application/json' },
            body: data
        });
        const json = await res.json();
        this.form = json.form;
    },
    async captureStill(){
        const file = `still-${this.stills.length}.png`
        const still = await this.$refs.canvas.captureStill(file);
        this.stills.push(still);

        const data = new FormData();
        data.append('csrf_token', this.csrf);
        data.append('attachments', still, file);
        fetch(this.formAction, { method: 'POST', headers: { 'accept': 'application/json' }, body: data }).then(res => console.log(res));
    },
    async upload(form){
        const { responseText } = await xhrUpload(form, p => this.progress = p);
        const { scan } = JSON.parse(responseText);
        this.scan = scan;
    },
    async pubSearch(event) {
        const query = event.target.value;
        const res = await fetch(`/publications?title=${query}`, { headers: { accept: 'application/json' } });
        this.pubList = await res.json();
    }
  },
  components: {
      Upload3D,
      'ctm-viewer': CtmViewer
  },
  template: `
    <form class="Upload__form Subgrid" :action="formAction" method="post" @submit.prevent="submit" enctype="multipart/form-data" novalidate style="display:contents">
    <link rel="stylesheet" href="/static/js/components/upload.css">
    <h1 class="Upload__title">Upload New</h1>
    <input type="hidden" name="csrf_token" :value="csrf">
        <span v-if="error" class="error">[{{ error }}]</span>
        <h2 class="Upload__section-title">1. Browse and preview STL file</h2>
        <div v-if="scan && scan.ctm" class="Subgrid" style="grid-column-start: 1; grid-column-end: 4; grid-auto-flow: dense">
            <ctm-viewer ref="canvas" :src="'/' + scan.ctm" height=400px width=500px></ctm-viewer>
            <span class="Upload__stills">
                2. Take Stills - Move image into appropriate position and click the button below (Minimum of 1 snapshot image, maximum of 6 images).

                <button type="button" @click="captureStill">Capture</button>

                <img v-for="url in stillUrls" :src="url" class="Upload__still" />
            </span>
        </div>
        <Upload3D v-else style="width: 100%; display: block;" @change="upload" :progress="progress"></Upload3D>
        <p>
            <h2 class="Upload__section-title">3. Scientific Name</h2>
            <input name="scientific_name" class="Upload__form-input" :value="form.scientific_name.data"/><br>
        </p>
        <fieldset>
            <legend><span class="Upload__section-title">4. Specimen</span> - Please enter relevant specimen information</legend>
            <p>
                Alt Name<br>
                <input name="alt_name" :value="form.alt_name.data" class="Upload__form-input" /><br>
            </p>
            <p>
            Specimen Location<br>
            <input type="text" name="specimen_location" :value="form.specimen_location.data" class="Upload__form-input" /><br>
            </p>
            <p>
            Specimen ID<br>
            <input type="text" name="specimen_id" :value="form.specimen_id.data" class="Upload__form-input" /><br>
        </p>
        </fieldset>
      <p>
        <h2 class="Upload__section-title">6. Description</h2>
        <textarea name="description" :value="form.description.data" class="Upload__form-input" /><br>
    </p>
    <fieldset>
        <legend><span class="Upload__section-title">7. Publications</span> - Assign any relevant publications to the scan</legend>
        <div class="SelectViewer">
            <div class="ListSearch">
                <div class="ListSearch__search Search">
                <input type="text" name="pub_query" class="Search__input"  @keyup="pubSearch" />
                <button name="pub_search" :value="form.pub_search.data" class="Search__submit">Search</button>
                </div>
                <div name="publications_search" class="ListSearch__results">
                  <ul>
                    <li v-for="pub in pubList"><input name="publications_search" type="checkbox" :value="pub.id">{{ pub.title }}</li>
                  </ul>
                </div>
            </div>
            <div name="publications" class="ListSearch__results">
            <ul>
                <li v-for="pub in savedPublications"><input name="publications" type="checkbox" :value="pub.id">{{ pub.title }}</li>
            </ul>
            </div>
        </div>
    </fieldset>
    <p>8. Categories - Assign the relevant tags to this entry. At least one catagory in each of Taxonomy, Geologic Age, Elements and Ontologic Age is required.</p>

    <fieldset>
        <legend>Geologic Age</legend>
        <ul>
            <li v-for="option in form.geologic_age.choices"><label><input type="checkbox" name="geologic_age" :value="option.id" :checked="(form.geologic_age.data || [] ).some(tag => option.id===tag.id)">{{ option.name }}</label></li>
        </ul>
    </fieldset>

    <fieldset>
        <legend>Ontogenic Age</legend>
        <ul>
            <li v-for="option in form.ontogenic_age.choices"><label><input type="checkbox" name="ontogenic_age" :value="option.id" :checked="(form.ontogenic_age.data || [] ).some(tag => option.id===tag.id)">{{ option.name }}</label></li>
        </ul>
    </fieldset>

        <p><button>Submit</button></p>
    </form>
    `
}
