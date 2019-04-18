const Tree = {
  name: 'Tree',
  props: ['items', 'childKey'],
  functional: true,
  render(h, context) {
    const children = [];
    const { items, childKey } = context.props;

    for (const item of items){
      const childItems = item[childKey];
      const nextLevel = childItems && h(Tree, { ...context.data, props: { items: childItems, childKey } });
      const extended = Object.create(item, {
        [childKey]: {
          value: { render: () => nextLevel }
        },
        hasChildren: {
          value: childItems && childItems.length
        }
      });

      const [li] = context.scopedSlots.node(extended);
      children.push(li);
    }
    return h('ul', context.data, children);
  }
}

export default Tree;
