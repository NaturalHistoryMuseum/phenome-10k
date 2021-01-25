Files {
	create({ bucket, location }){
		return bucket+location
	}
}

Scans {
	create({ scientificName, fileId }) {

	}
}


payload: {
	scientificName,
	fileName,
	fileData
}

POST /upload


function Scans(sql) {
	return {
		create(data) {
			await sql`INSERT INTO file (
				filename,
				location,
				owner_id,
				mime_type,
				size,
				storage_area
			)
			VALUES (
				${data.file.filename},
				${data.file.location},
				${data.authorId},
				${data.file.mimeType},
				${data.file.size},
				${data.file.storageArea}
			)`;

			const id = sql.getLastId();

			sql`INSERT INTO scan (
				author_id,
				scientific_name,
				published,
				url_slug,
				file_id,
				alt_name,
				speciment_id,
				specimen_location,
				specimen_link,
				description
			);


			sa.Column('id', sa.Integer(), nullable=False),
			sa.Column('gbif_id', sa.Integer(), nullable=True),
			sa.Column('author_id', sa.Integer(), nullable=True),
			sa.Column('date_created', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
			sa.Column('date_modified', sa.DateTime(), nullable=True),
			sa.Column('scientific_name', sa.String(length=250), nullable=True),
			sa.Column('published', sa.Boolean(), nullable=True),
			sa.Column('url_slug', sa.String(length=250), nullable=True),
			sa.Column('alt_name', sa.String(length=250), nullable=True),
			sa.Column('file_id', sa.Integer(), nullable=True),
			sa.Column('ctm_id', sa.Integer(), nullable=True),
			sa.Column('specimen_id', sa.String(length=250), nullable=True),
			sa.Column('specimen_location', sa.String(length=250), nullable=True),
			sa.Column('specimen_link', sa.String(length=250), nullable=True),
			sa.Column('description', sa.Text(), nullable=True),
		}
	}
}
