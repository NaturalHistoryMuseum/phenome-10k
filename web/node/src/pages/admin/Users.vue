<template>
  <div :class="$style.main">
    <h1 class="Body__title">Manage Users</h1>
    <div class="Body__filters">
      <div>{{ routeData.error }}</div>
      <div v-if="userFilters" :class="$style.sort">
        <ul :class="$style.sortList">
          <li @click="$router.replace({query: {}})">
            Clear all
          </li>
          <li v-for="(value, name) in userFilters">
            {{ name }}: {{ value }}
          </li>
        </ul>
      </div>
    </div>
    <div class="Body__content">
      <div :class="$style.table">
        <div :class="[$style.tableRow, $style.tableHeader]">
          <div>Name</div>
          <div>Email</div>
          <div>Registered</div>
          <div @click="addParam('role', 'ADMIN')">Admin</div>
          <div @click="addParam('role', 'CONTRIBUTOR')">Contributor</div>
          <div>Country</div>
          <div>User type</div>
        </div>
        <div v-for="user in users" :key="user.id" :class="$style.tableRow">
          <div>{{ user.name }}</div>
          <div>{{ user.email }}</div>
          <div>{{ date(user.date_registered) }}</div>
          <div>
            <i class="fas" :class="user.admin ? 'fa-check' : 'fa-times'" @click="toggleRole('ADMIN', !user.admin, user.id)"></i>
          </div>
          <div>
            <i class="fas" :class="user.contributor ? 'fa-check' : 'fa-times'" @click="toggleRole('CONTRIBUTOR', !user.contributor, user.id)"></i>
          </div>
          <div :class="$style.flag" @click="addParam('country_code', user.country_code)">
            <CountryFlag v-if="user.country_code" :country="user.country_code" size="normal" />
          </div>
          <div @click="addParam('user_type', user.user_type)">{{ user.user_type }}</div>
        </div>
      </div>
      <Pagination :page="page"
                  :total="totalPages"
                  :to="changePage"
                  class="Body__pagination" />
    </div>
  </div>
</template>

<script>
import Page from '../common/base/Page';
import CountryFlag from 'vue-country-flag';

export default {
  extends: Page,
  components: {
    CountryFlag
  },
  data() {
    return {};
  },
  computed: {
    users() {
      return this.$route.meta.data.users;
    },
    totalPages() {
      return Math.ceil(this.$route.meta.data.total / this.$route.meta.data.pageSize);
    },
    page() {
      return Math.ceil(this.$route.meta.data.offset / this.$route.meta.data.pageSize) + 1;
    },
    userFilters() {
      return this.$route.meta.data.filters;
    }
  },
  methods: {
    date(strDate) {
      return new Date(strDate).toLocaleDateString();
    },
    addParam(name, value) {
      let q = { ...this.$route.query };
      q[name] = value;
      this.$router.replace({ query: q });
    },
    changePage(page) {
      let q = { ...this.$route.query };
      q['offset'] = (page - 1) * this.$route.meta.data.pageSize;
      return { name: this.$route.name, query: q };
    },
    toggleRole(roleName, addRole, userId) {
      fetch('/change-role', {
        method: 'POST',
        mode: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: roleName, action: addRole ? 'ADD' : 'REMOVE', user_id: userId })
      }).then((r) => {
        if (r.ok) {
          window.location.reload()
        }
      });
    }
  }
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

@import '../common/styles/sort';

.main {
  display: contents;
}

.table {
  display: grid;
  grid-template-columns: [name] 1fr [email] 1fr [registered] auto [admin] auto [contributor] auto [flag] auto [usertype] auto;
  grid-template-rows: auto;
  grid-auto-rows: 1fr;
  grid-gap: 10px;
  align-items: center;
  margin-top: 20px;
  font-size: $small-font-size;
}

.tableRow {
  display: contents;

  &.tableHeader {
    font-weight: bold;
    color: $palette-grey-1;
    text-transform: uppercase;
    font-size: $small-font-size;
  }

  & > * {
    padding: 2px;

    &:nth-child(1), &:nth-child(2) {
      // wrap the long strings (name and email)
      word-break: break-all;
    }

    &:nth-child(4), &:nth-child(5), &:nth-child(6) {
      // center the flag and ticks/crosses
      justify-self: center;
      cursor: pointer;
    }
  }

  & select, & option {
    @include font-body;
    font-size: $small-font-size;
  }
}

.editButton {
  padding-left: 5px;
  opacity: 0.6;
}

.sortList li {
  &:first-child {
    cursor: pointer;
  }

  &:not(:last-child) {
    margin-right: 2em;
  }
}
</style>
