async function render(renderer, url, defaultData){
	const context = { url, defaultData };
	const html = await renderer.renderToString(context);
	// NB the context object gets populated with some utility
	// functions by the vue-loader

	// Don't forget to escape < characters to stop attackers
	// closing the script tag early, allowing injection attacks.
	const defaultJSON = JSON.stringify(defaultData).replace(/</g, '\\u003C');

	return (
		`${context.renderResourceHints()}
		${context.renderStyles()}
		${html}
		<script>window.p10k_defaultData = ${defaultJSON};</script>
		${context.renderScripts()}`
	);
}

module.exports = renderer => (url, defaultData) => render(renderer, url, defaultData);
