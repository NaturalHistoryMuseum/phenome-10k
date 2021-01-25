const path = require('path');
const fs= require('fs');
const uuidv4 = require('uuid').v4;

// Start with a few helper functions

/**
 * Write a stream to the filesystem and return a promise that resolves on complete
 * @param {string} path The filepath to write to
 * @param {Stream} data The stream to write to file
 * @param {string} flags The flags to open the file with
 */
function writeStream(path, data, flags) {
	const stream = fs.createWriteStream(path, { flags });
	const promise =  new Promise((resolve, reject) => {
		stream.on('finish', resolve);
		stream.on('error', reject);
	});
	data.pipe(stream);
	return promise;
}

/**
 * Writes data or a stream to the filesystem, returns a promies that resolves when done
 * @param {string} path The filepath to write to
 * @param {Stream|string|Buffer} data The data or stream to write to file
 * @param {string} flag The flags to open the file with
 */
function writeFile(path, data, flag) {
	if(data && data.pipe) {
		return writeStream(path, data, flag);
	} else {
		return fs.promises.writeFile(path, data, { flag });
	}
}

/**
 * Creates a new file and writes data to it.
 * If the file already exists, it is not overwritten
 * @async
 * @param {string} id The filepath to create
 * @param {Stream|string|Buffer} data The initial data to write to the file
 * @returns True on success, false if the file exists and no data was written
 */
async function createNew(id, data) {
	try {
		// wx = create file if it doesn't exist, throw an error if it does exist
		await writeFile(id, data, 'wx');
		return true;
	} catch(e) {
		if(e.code === 'EEXIST') {
			return false;
		}

		throw e;
	}
}

/**
 * Create an instance of the fs object store
 * @param {string} location The directory to save all files in
 * @returns {FsStore}
 */
const FsStore = (location) => {
	// Cheeky helper to get the full path for a file
	const getPath = file => path.join(location, file);

	return {
		/**
		 * Create a new data file and return its ID
		 * @param {String|Buffer|Stream} data The initial data to write to the file
		 * @param {string} id Optional string to base the file ID on
		 * @returns {string} ID of the new file
		 */
		async create(data, id = uuidv4()) {
			// Files should be saved in the location /yyyy/mm/dd/name.ext
			const now = new Date;
			const d = String(now.getDate()).padStart(2, '0');
			const m = String(now.getMonth()+1).padStart(2, '0');
			const y = String(now.getFullYear());
			const directory = path.join(y, m, d);

			// Create the date directory if it doesn't exist
			await fs.promises.mkdir(getPath(directory), { recursive: true });

			// Split the requested filename and extension
			const {ext, name} = path.parse(id);

			// Sanitize the base filename or generate with uuidv4
			const filename = name.replace(/[^a-z0-9_-]+/g, '') || uuidv4();

			// Concat with date directory
			const base = path.join(directory, filename);

			// Ensure we don't overwrite duplicates
			// Try to create name.ext, fall back to name-n.ext if it already exists, where n is a number
			let count = 0;
			let uid = base+ext;

			// Keep trying to create until we come up with a filename that doesn't exist
			while(!await createNew(getPath(uid), data)) {
				count++;
				uid = `${base}-${count}${ext}`;
			}

			// Done, return the ID
			return uid;
		},
		/**
		 * Overwrite an existing file. Throws if the file doesn't exist
		 * @param {string} id File ID of file to write to
		 * @param {String|Buffer|Stream} data Data to write to the file
		 */
		async write(id, data) {
			// r+ = open file for writing (and reading) if it exists, throw an error if it doesn't
			await writeFile(getPath(id), data, 'r+');
		},
		/**
		 * Get a read stream for the given file
		 * @param {string} id File ID to read
		 * @returns {fs.ReadStream} Stream for file
		 */
		async read(id) {
			const stream = fs.createReadStream(getPath(id));

			await new Promise((resolve, reject) => {
				stream.on('error', reject);
				stream.on('ready', resolve)
			});

			return stream;
		},
		/**
		 * Delete a file from the filesystem
		 * @param {String} id ID of file to delete
		 */
		async delete(id) {
			await fs.promises.unlink(getPath(id));
		},

		async sizeOf(id) {
			const { size } = await fs.promises.stat(id);

			return size;
		}
	}
}

/*
const FileBucket = store => {
	return {
		create(data, id) {
			return FileObject(store, store.create(data, id))
		}
	}
}

const FileObject = (store, id) => {
	return {
		id,
		put(data) {
			return store.write(id, data);
		},
		read() {
			return store.read(id);
		},
		delete(){
			return store.delete(id);
		},
		sizeOf(){
			return store.sizeOf(id);
		}
	}
}*/

module.exports = FsStore;
