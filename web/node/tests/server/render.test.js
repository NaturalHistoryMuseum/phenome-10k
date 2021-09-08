const render = require('../../server/render');

test('Renders data', async () => {
	const renderer = {
		renderToString: jest.fn((context)=>{
			context.renderResourceHints = () => '[resource hints]';
			context.renderStyles = () => '[styles]';
			context.renderScripts = () => '[scripts]';
			return `[rendered context
	url: ${context.url}
	defaultData: ${context.defaultData}
]`;
		})
	};
	const url = '/etc';
	const defaultData = {a:1};

	expect(await render(renderer)(url, defaultData)).toMatchSnapshot();
});
