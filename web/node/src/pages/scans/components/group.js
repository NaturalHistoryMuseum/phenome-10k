import Results from './Results';

const Group = {
  name: 'Group',
  props: ['name', 'items'],
  render(h) {
    return h('div', [
      this.name,
      h(Results, { props: { results: this.items } })
    ]);
  }
};

export default Group;
