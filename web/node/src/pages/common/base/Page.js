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
        routeData() {
            return this.$route.meta.data;
        },
        page() {
            return this.routeData.page;
        },
        totalPages() {
            return this.routeData.total_pages;
        },
    },
    methods: {}
};
