<template>
  <div>
    <h1>Manage Users</h1>
    {{ $route.meta.data.error }}
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Registered</th>
          <th>Role</th>
          <th>Country</th>
          <th>User type</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.name }}</td>
          <td>{{ user.email }}</td>
          <td>{{ date(user.date_registered) }}</td>
          <td>
            <form method="POST">
              <select name="role" v-model="user.role">
                <option>USER</option>
                <option>CONTRIBUTOR</option>
                <option>ADMIN</option>
              </select>
              <button name="id" :value="user.id">Save</button>
            </form>
          </td>
          <td><img :src="`https://www.countryflags.io/${user.country_code}/flat/48.png`" :alt="user.country_code"></td>
          <td>{{ user.user_type }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data(){
    return {
      users: this.$route.meta.data.users
    }
  },
  methods: {
    date(strDate){
      return new Date(strDate).toLocaleDateString()
    }
  }
}
</script>
