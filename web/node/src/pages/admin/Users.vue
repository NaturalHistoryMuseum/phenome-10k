<template>
  <div :class="$style.main">
    <h1 class="Body__title">Manage Users</h1>
    <div class="Body__filters">
      {{ routeData.error }}
    </div>
    <div class="Body__content">
      <div :class="$style.table">
        <div :class="[$style.tableRow, $style.tableHeader]">
          <div>Name</div>
          <div>Email</div>
          <div>Registered</div>
          <div>Role</div>
          <div>Country</div>
          <div>User type</div>
        </div>
        <div v-for="user in users" :key="user.id" :class="$style.tableRow">
          <div>{{ user.name }}</div>
          <div>{{ user.email }}</div>
          <div>{{ date(user.date_registered) }}</div>
          <div>
            <form method="POST" class="p10k__form">
              <div>
                <select name="role" v-model="user.role" @change="changedRoles.push(user.id)">
                  <option>USER</option>
                  <option>CONTRIBUTOR</option>
                  <option>ADMIN</option>
                </select>
              </div>
              <div>
                <button name="id" :value="user.id" v-if="changedRoles.includes(user.id)">Save</button>
              </div>
            </form>
          </div>
          <div :class="$style.flag"><img v-if="user.country_code" :src="`https://www.countryflags.io/${user.country_code}/flat/48.png`"
                    :alt="user.country_code"></div>
          <div>{{ user.user_type }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Page from '../common/base/Page';

export default {
  extends: Page,
  data() {
    return {
      users: this.$route.meta.data.users,
      changedRoles: []
    };
  },
  methods: {
    date(strDate) {
      return new Date(strDate).toLocaleDateString();
    }
  }
};
</script>

<style module lang="scss">
@import 'scss/palette';
@import 'scss/fonts';

.main {
  display: contents;
}

.table {
  display: grid;
  grid-template-columns: [name] 1fr [email] 1fr [registered] auto [role] auto [flag] auto [usertype] auto;
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

    &:nth-child(1), &:nth-child(2){
      // wrap the long strings (name and email)
      word-break: break-all;
    }

    &:nth-child(5) {
      // center the flag
      justify-self: center;
    }
  }

  & select, & option {
    @include font-body;
    font-size: $small-font-size;
  }
}

.flag {
  line-height: 1;
}
</style>
