import Pagination from '../Pagination';
import Search from '../forms/Search';

export default {
    name: 'Page',
    components: {
        Pagination,
        Search
    },
    data: function () {
        return {
            q: this.$route.meta.data.q
        };
    },
    computed: {
        data() {
            return this.$route.meta.data;
        },
        page() {
            return this.$route.meta.data.page;
        },
        totalPages() {
            return this.$route.meta.data.total_pages;
        },
    },
    methods: {}
};
