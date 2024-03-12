import Page from './Page';

export default {
  name: 'Manage',
  extends: Page,
  data() {
    return {
      warningMsg: 'This action will permenently delete this record.',
    };
  },
  computed: {
    items() {
      return [];
    },
    filterQ() {
      return null;
    },
    filterOptions() {
      return [];
    },
  },
  methods: {
    /**
     * Ask the user to confirm whether they want to delete the record, prevent form sub if not
     * @param e {Event} The form submit event
     */
    confirmDelete(e) {
      if (!confirm()) {
        e.preventDefault(this.warningMsg);
      }
    },
    /**
     * Generate the CSS class for a side filter link (e.g. letters/years)
     */
    getFilterClass(filterText) {
      let classes = {};
      classes[this.$style.sideFilter] = true;
      classes[this.$style['sideFilter--active']] = this.filterQ === filterText;
      return classes;
    },
  },
};
