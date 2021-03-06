<template>
  <q-card v-if="user.authorized">
    <q-list :class="{'q-py-md': true, 'q-px-md': $q.screen.gt.xs}">
      <q-item dense :disable="loading">
        <q-item-section avatar>
          <tg-avatar :size="$q.screen.gt.xs ? '64px' : '32px'" :src="user.photo" />
        </q-item-section>
        <q-item-section>
          <q-item-label>{{user.fullname}}</q-item-label>
          <q-item-label caption>{{sources}} channels<span v-if="$q.screen.gt.xs"> available</span></q-item-label>
        </q-item-section>
        <q-item-section side>
          <confirm-button :size="$q.screen.gt.xs ? 'md' : 'sm'" round color="negative" icon="exit_to_app" @confirm="logout" title="Stop reposting and logout"/>
        </q-item-section>
        <q-item-section side>
          <q-btn flat round :size="$q.screen.gt.xs ? 'lg' : 'md'" :loading="loading" icon="refresh" @click="reload" title="Refresh user info and channels"/>
        </q-item-section>
      </q-item>
    </q-list>
  </q-card>
  <q-card v-else>
    <q-list :class="{'q-py-md': true, 'q-px-md': $q.screen.gt.xs}">
      <q-item dense ripple clickable @click="showForm = true">
        <q-item-section avatar>
          <q-avatar :size="$q.screen.gt.xs ? '64px' : '32px'">
            <img src="~assets/Telegram_logo.svg" />
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>Login to Telegram to continue</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
    <q-list v-if="showForm" :class="{'row': true, 'q-py-md': true, 'q-px-md': $q.screen.gt.xs}">
      <q-list class="offset-md-4 col-md-4 offset-sm-3 col-sm-6 offset-xs-1 col-xs-10">
        <q-item>
          <q-input class="full-width" v-model="tel" type="tel" mask="###############" label="Phone number"
            :rules="[v => v.length > 8 || 'Please enter a phone number in international format']" lazy-rules
            :readonly="loading||stage > 0" @keyup.enter="login"/>
        </q-item>
        <q-item v-if="stage > 0">
          <q-input class="full-width" v-model="code" type="text" mask="######" label="Confirmation code"
            :readonly="loading||stage > 1" @keyup.enter="login"/>
        </q-item>
        <q-item v-if="stage > 1">
          <q-input class="full-width" v-model="pwd" type="password" label="2FA Password"
          :readonly="loading"  @keyup.enter="login"/>
        </q-item>
      </q-list>
    </q-list>
    <q-card-actions align="right" v-if="showForm">
      <q-btn id="submit-btn" color="primary" :loading="loading" @click="login">Submit</q-btn>
    </q-card-actions>
  </q-card>
</template>

<script>
import AuthMixin from 'components/auth-mixin'
import ConfirmButton from 'components/confirm-button'
import TgAvatar from 'components/tg-avatar'

export default {
  // name: 'ComponentName',
  components: { ConfirmButton, TgAvatar },
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
            this.showForm = false
            this.stage = 0
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
      if (!this.user.authorized) return

      this.loading = true
      Promise.all([
        this.$store.dispatch('tguser/load'),
        this.$store.dispatch('sources/load')
      ]).catch(this.$errorNotify)
        .finally(() => { this.loading = false })
    }
  },
  mounted () {
    if (this.user.authorized && !this.user.fullname) this.reload()
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
