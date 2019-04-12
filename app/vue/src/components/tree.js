const Tree = {
  name: 'Tree',
  props: ['items', 'childKey'],
  functional: true,
  render(h, context) {
    const children = [];
    const { items, childKey } = context.props;

    for (const item of items){
      const [li] = context.scopedSlots.node(item);
      const childItems = item[childKey];
      if(childItems) {
        li.children.push(h(Tree, { ...context.data, props: { items: childItems, childKey } }));
      }
      children.push(li);
    }
    return h('ul', context.data, children);
  }
}

export default Tree;
