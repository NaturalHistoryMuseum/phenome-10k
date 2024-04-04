import Page from './Page';

export default {
  name: 'Library',
  extends: Page,
  methods: {
    /**
     * Get the router-link `to` param for "View Mine"/"View All" links
     * @param {boolean} mine true = view mine, false = view all
     */
    getMineLink(mine) {
      const query = Object.assign({}, this.$route.query);
      // We only care about the presence of the `mine` parameter, not its value
      if (mine) {
        query.mine = null;
      } else {
        delete query.mine;
      }

      return {
        query,
      };
    },
    /**
     * Get the css class for the "View Mine"/"View All" links
     * @param {bool} mine true=view mine, false = view all
     */
    getMineLinkClass(mine) {
      const cls = this.$style.sortItem;

      return {
        [cls]: true,
        [`${cls}--active`]: mine === 'mine' in this.$route.query,
      };
    },
    getSortLink(sort) {
      const query = Object.assign({}, this.$route.query);
      query.sort = sort;
      return {
        query,
      };
    },
    getSortLinkClass(field) {
      const cls = this.$style.sortItem;

      return {
        [cls]: true,
        [`${cls}--active`]: (this.$route.query.sort || 'name') === field,
      };
    },
  },
};
