export default {
  methods: {
    is_authorized () {
      return !!this.$auth.getToken()
    },
    has_role (role) {
      const user = this.$auth.getTokenPayload()
      const roles = (user && user.aud) || ['guest']
      return roles.includes(role)
    }
  }
}
