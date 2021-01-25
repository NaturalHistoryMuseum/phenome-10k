function FileMeta(sql) {

	return {
		create(data) {
			await sql`INSERT INTO files (filename, location, owner_id, mime_type, size, storage_area) VALUES(${data.filename}, ${data.location}, ${data.ownerId}, ${data.mimeType}, ${data.size}, ${data.storageArea})`;
			const [{id}] = await sql`SELECT id FROM files WHERE location=${data.location} LIMIT 1`;
			return id;
		}
	}
}
