<template>
  <q-card bordered dark class="bg-vk">
    <q-card-section v-if="is_authorized()">
      <q-item dense dark :disable="loading">
        <q-item-section avatar>
          <q-avatar size="64px">
            <img v-if="user.photo" :src="user.photo" />
            <img v-else src="~assets/VK_Monochrome_Logo.svg" />
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>{{user.fullname}}</q-item-label>
          <q-item-label caption>{{targets}} groups available</q-item-label>
        </q-item-section>
        <q-item-section side>
          <confirm-button round color="grey" icon="exit_to_app" @confirm="logout" title="Logout"/>
        </q-item-section>
        <q-item-section side>
          <q-btn flat round size="lg" :loading="loading" icon="refresh" @click="reload" title="Refresh"/>
        </q-item-section>
      </q-item>
    </q-card-section>
    <q-card-section v-else>
      <q-item clickable dark dense ripple @click="login" :disable="loading">
        <q-item-section side>
          <q-avatar size="64px">
            <img src="~assets/VK_Monochrome_Logo.svg" />
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>Login to VK account to continue</q-item-label>
        </q-item-section>
        <q-item-section side v-if="loading">
          <q-spinner size="3em" color="white"/>
        </q-item-section>
      </q-item>
    </q-card-section>
  </q-card>
</template>

<script>
import AuthMixin from 'components/auth-mixin'
import ConfirmButton from 'components/confirm-button'

export default {
  // name: 'ComponentName',
  components: { ConfirmButton },
  mixins: [AuthMixin],
  data () {
    return {
      loading: false
    }
  },
  computed: {
    targets () {
      return this.$store.state.targets.list.length
    },
    user () {
      return this.$store.state.vkuser
    }
  },
  methods: {
    login: function () {
      this.loading = true
      console.debug('VK login procedure...')
      this.$http
        .get(this.$eps.login, { params: { back_url: window.location.href } })
        .then(resp => {
          console.debug('Redirecting to', resp.data.auth_url)
          if (resp.data.auth_url) window.location = resp.data.auth_url
        })
        .catch(this.$errorNotify)
        .finally(() => { this.loading = false })
    },
    logout: function () {
      console.debug('VK logout procedure...')
      this.$auth.clearToken()
      this.$store.commit('connections/reset')
      this.$store.commit('targets/reset')
      this.$store.commit('sources/reset')
      this.$store.commit('tguser/reset')
      this.$store.commit('vkuser/reset')
      this.$root.$emit('authorization')
    },
    reload: function () {
      this.loading = true
      Promise.all([
        this.$store.dispatch('vkuser/load'),
        this.$store.dispatch('targets/load')
      ]).catch(this.$errorNotify)
        .finally(() => { this.loading = false })
    }
  },
  created () {
    let state = window.location.hash
    state = state.substring(state.indexOf('login_state=') + 12)

    if (state) {
      this.loading = true
      console.debug('VK Login state:', state)
      this.$http.get(this.$eps.login, { params: { state } })
        .then(resp => {
          if (resp.ok && resp.data.token) {
            this.$auth.setToken(resp.data.token)
            this.$root.$emit('authorization')
            this.reload()
          }
        })
        .catch(err => {
          this.loading = false
          this.$errorNotify(err)
        })
        .finally(() => window.history.replaceState(null, document.title, '/'))
    }
  },
  mounted () {
    if (this.is_authorized() && !this.user.id) this.reload()
  }
}
</script>

<style>
.bg-vk {
  background-color: #4680C2;
}
</style>
