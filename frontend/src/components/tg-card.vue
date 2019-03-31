<template>
  <q-card bordered v-if="user.authorized">
    <q-card-section>
      <q-item dense :disable="loading">
        <q-item-section avatar>
          <q-avatar size="64px">
            <img v-if="user.photo" :src="user.photo" />
            <img v-else src="~assets/Telegram_logo.svg" />
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>{{user.fullname}}</q-item-label>
          <q-item-label caption>{{sources}} channels available</q-item-label>
        </q-item-section>
        <q-item-section side>
          <confirm-button round color="grey" icon="exit_to_app" @confirm="logout" title="Logout"/>
        </q-item-section>
        <q-item-section side>
          <q-btn flat round size="lg" :loading="loading" icon="refresh" @click="reload" title="Refresh"/>
        </q-item-section>
      </q-item>
    </q-card-section>
  </q-card>
  <q-card bordered v-else>
    <q-card-section>
      <q-item dense ripple clickable @click="showForm = true">
        <q-item-section avatar>
          <q-avatar size="64px">
            <img src="~assets/Telegram_logo.svg" />
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>Login to Telegram to continue</q-item-label>
        </q-item-section>
      </q-item>
    </q-card-section>
    <q-card-section v-if="showForm" class="q-px-xl">
      <q-input v-model="tel" type="tel" mask="###############" label="Phone number" lazy-rules
        :rules="[v => v.length > 8 || 'Please enter a phone number in international format']"
        :readonly="loading||stage > 0"/>
    </q-card-section>
    <q-card-section v-if="stage > 0" class="q-px-xl">
      <q-input v-model="code" type="text" mask="######" label="Confirmation code"
        :readonly="loading||stage > 1"/>
    </q-card-section>
    <q-card-section v-if="stage > 1" class="q-px-xl">
      <q-input v-model="pwd" type="password" label="2FA Password" :readonly="loading" />
    </q-card-section>
    <q-card-actions align="right" v-if="showForm">
      <q-btn id="submit-btn" color="primary" :loading="loading" @click="login">Submit</q-btn>
    </q-card-actions>
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
      showForm: false,
      stage: 0,
      loading: false,
      tel: '',
      code: '',
      pwd: ''
    }
  },
  computed: {
    sources () {
      return this.$store.state.sources.list.length
    },
    user () {
      return this.$store.state.tguser
    }
  },
  methods: {
    login () {
      console.debug('TG login procedure...')
      this.loading = true
      let payload = { phone: this.tel }
      if (this.stage) payload.code = this.code
      if (this.stage > 1) payload.password = this.pwd

      this.$http.post(this.$eps.tgauth, payload)
        .then(resp => {
          if (resp.data.authorized) {
            this.$store.commit('tguser/fill', resp.data)
            this.$store.dispatch('sources/load')
          } else {
            if (resp.data['2fa']) this.stage = 2
            else if (resp.data['code']) this.stage = 1
          }
        })
        .catch(this.$errorNotify)
        .finally(() => { this.loading = false })
    },
    logout: function () {
      console.debug('TG logout procedure...')
      this.$http
        .delete(this.$eps.tgauth)
        .then(resp => {
          this.$store.commit('tguser/reset')
          this.$store.commit('sources/reset')
        })
        .catch(this.$errorNotify)
    },
    reload: function () {
      this.loading = true
      Promise.all([
        this.$store.dispatch('tguser/load'),
        this.$store.dispatch('sources/load')
      ]).catch(this.$errorNotify)
        .finally(() => { this.loading = false })
    }
  },
  mounted () {
    if (!this.user.fullname) this.reload()
  }
}
</script>

<style>
.bg-tg {
  background-color: #0088cc;
}
#submit-btn {
  padding: 0 48px;
}
</style>
