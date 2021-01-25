const FsStore = require('.');
const { Readable } = require('stream');

const object = FsStore('/tmp/object-store');

test('creates object file', async ()=>{
	const uuid = await object.create('some random data');

	const stream = await object.read(uuid);

	let data = '';
	for await(const chunk of stream){
		data+=chunk;
	}

	expect(data).toEqual('some random data');
})

test('creates named file', async ()=> {
	const uuid = await object.create('named file', 'file-name.example');

	const date = new Date;
	const dir = `${date.getFullYear()}/${String(date.getMonth()+1).padStart(2,0)}/${String(date.getDate()).padStart(2,0)}/`;

	expect(uuid).toEqual(dir+'file-name.example');

	const uuid2 = await object.create('second named file', 'file-name.example');

	expect(uuid2).toEqual(dir+'file-name-1.example');
});

test('writes stream data', async ()=> {
	const stream = Readable.from(['a readable stream']);

	const uuid = await object.create(stream);

	let data = '';
	for await(const chunk of await object.read(uuid)){
		data+=chunk;
	}

	expect(data).toEqual('a readable stream')
});

test('overwrites file', async()=>{
	const uid = await object.create('x');

	await object.write(uid, 'y');

	let data = '';
	for await(const chunk of await object.read(uid)){
		data+=chunk;
	}

	expect(data).toEqual('y')
});

test('deletes file', async()=>{
	const uid = await object.create('x');

	await object.delete(uid);

	expect(object.read(uid)).rejects.toThrow();
});

afterAll(()=>{
	require('fs').rmdirSync('/tmp/object-store', { recursive: true });
});
