function Files(objects, fileMeta) {
	return {
		create(meta, data) {
			const location = await objects(meta.storageArea).create(data, meta.filename);
			const size = await objects.sizeOf(location);
			const id = await fileMeta.create({ ...meta, location, size });
			return id;
		}
	}
}
