import html from 'encode-html-template-tag';

export default async function batchUpload({ inputName, files }) {
  return {
    menu: 'library',
    title: 'Batch upload',
    content: await html` <form method="POST" enctype="multipart/form-data">
      ${JSON.stringify(files)}
      <label
        >Add files <input name="${inputName}" type="file" multiple
      /></label>
      <button>Upload</button>
    </form>`.render(),
  };
}

// batchUpload.parse = formData => formData.getAll('source');
