<template>
  <q-card>
    <q-list v-if="is_authorized()" dark :class="{'bg-vk': true, 'q-py-md': true, 'q-px-md': $q.screen.gt.xs}">
      <q-item dense dark :disable="loading">
        <q-item-section avatar>
          <q-avatar :size="$q.screen.gt.xs ? '64px' : '32px'">
            <img v-if="user.photo" :src="user.photo" />
            <img v-else src="~assets/VK_Monochrome_Logo.svg" />
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>{{user.fullname}}</q-item-label>
          <q-item-label caption>{{targets}} groups<span v-if="$q.screen.gt.xs"> available</span></q-item-label>
        </q-item-section>
        <q-item-section side>
          <confirm-button :size="$q.screen.gt.xs ? 'md' : 'sm'" round color="negative" icon="stop" @confirm="completeLogout" title="Stop reposting and logout"/>
        </q-item-section>
        <q-item-section side>
          <confirm-button :size="$q.screen.gt.xs ? 'md' : 'sm'" round color="grey" icon="exit_to_app" @confirm="logout" title="Logout"/>
        </q-item-section>
        <q-item-section side>
          <q-btn flat round :size="$q.screen.gt.xs ? 'lg' : 'md'" :loading="loading" icon="refresh" @click="reload" title="Refresh user info and groups"/>
        </q-item-section>
      </q-item>
    </q-list>
    <q-list v-else dark :class="{'bg-vk': true, 'q-py-md': true, 'q-px-md': $q.screen.gt.xs}">
      <q-item clickable dark dense ripple @click="open=true" :disable="loading">
        <q-item-section side>
          <q-avatar :size="$q.screen.gt.xs ? '64px' : '32px'">
            <img src="~assets/VK_Monochrome_Logo.svg" />
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>Login to VK account<span v-if="!open">: click to continue</span>...</q-item-label>
        </q-item-section>
        <q-item-section side v-if="loading">
          <q-spinner size="3em" color="white"/>
        </q-item-section>
      </q-item>
    </q-list>
    <q-list v-if="open" :class="{'q-py-md': true, 'q-px-md': $q.screen.gt.xs}">
      <q-list>
        <q-item>
          <q-item-section avatar>
            <q-icon :name="stage < 1 ? 'radio_button_unchecked' : 'check_circle_outline'" color="grey-5"/>
          </q-item-section>
          <q-item-section>
            <q-item-label>
              Click <span @click="$refs['proceed-btn'].click()" class="text-primary text-uppercase q-px-xs">proceed</span> to open VK app permissions page.
              Watch for blocked popup<q-icon class="desktop-only" name="arrow_upward" size="2em" color="primary"/>.
            </q-item-label>
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section avatar>
            <q-icon :name="stage < 2 ? 'radio_button_unchecked' : 'check_circle_outline'" color="grey-5"/>
          </q-item-section>
          <q-item-section>
            <q-item-label lines="3">
              If you agree, you'll get redirected to address like this:
              <em class="text-grey-7">https://api.vk.com/blank.html#code=xxxxxxxxxxxxxxxxxx</em>
            </q-item-label>
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section avatar>
            <q-icon :name="stage < 3 ? 'radio_button_unchecked' : 'check_circle_outline'" color="grey-5"/>
          </q-item-section>
          <q-item-section>
            <q-input v-model="code" type="url" color="grey-10" class="full-width" ref="code-input"
              label="Copy that address and paste it here to finish the login process"
              lazy-rules :rules="[this.validateUrl]"
              @change="proceed" @focus="stage2" @keyup.enter="proceed"/>
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section avatar class="bg-amber-1 q-py-sm">
            <q-icon name="info" color="grey-5"/>
          </q-item-section>
          <q-item-section class="bg-amber-1 q-py-sm text-weight-light">
            <q-item-label>
              Unfortunately, this is the only way to get <em>post</em> permission from VK
            </q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-list>
    <q-separator v-if="open"/>
    <q-card-actions v-if="open" align="right">
      <q-btn flat color="primary" id="proceed-btn" ref="proceed-btn"
        :loading="loading" @click="proceed">Proceed</q-btn>
    </q-card-actions>
  </q-card>
</template>

<script>
import AuthMixin from 'components/auth-mixin'
import ConfirmButton from 'components/confirm-button'
import { openURL } from 'quasar'

let re = new RegExp('(?:https://api\\.vk\\.com/blank\\.html#code=)?(\\w{14,32})')

export default {
  // name: 'ComponentName',
  components: { ConfirmButton },
  mixins: [AuthMixin],
  data () {
    return {
      open: false,
      loading: false,
      code: '',
      stage: 0
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
    validateUrl: function (val) {
      return re.test(val) || 'This doesn\'t seem to be a valid URL with the code'
    },
    proceed: function () {
      if (this.code) {
        this.stage = 2
      } else {
        this.stage = 0
        this.$refs['code-input'].resetValidation()
      }
      switch (this.stage) {
        case 0:
          this.startLogin()
          this.stage = 1
          break
        case 2:
          let code = this.code.match(re)
          if (code) {
            this.finishLogin(code[1])
            this.stage = 3
          }
          break
        default:
          break
      }
    },
    stage2: function () {
      this.stage = 2
    },
    startLogin: function () {
      this.loading = true
      console.debug('VK login procedure...')
      this.$http
        .get(this.$eps.login)
        .then(resp => {
          console.debug('Opening', resp.data.auth_url)
          if (resp.data.auth_url) openURL(resp.data.auth_url)
        })
        .catch(this.$errorNotify)
        .finally(() => { this.loading = false })
    },
    finishLogin: function (code) {
      this.loading = true
      console.debug('Finishing VK login procedure...')
      this.$http
        .get(this.$eps.login, { params: { code } })
        .then(resp => {
          console.debug(resp)
          if (resp.ok && resp.data.token) {
            this.$auth.setToken(resp.data.token)
            this.$store.commit('tguser/fill', { authorized: resp.data.tgauth })
            this.$root.$emit('authorization')
            this.reload()
          }
        })
        .catch(this.$errorNotify)
        .finally(() => {
          this.loading = false
          this.stage = 0
          this.code = ''
          this.open = false
          this.$refs['code-input'].resetValidation()
        })
    },
    logout: function () {
      this.$store.commit('connections/reset')
      this.$store.commit('targets/reset')
      this.$store.commit('sources/reset')
      this.$store.commit('tguser/reset')
      this.$store.commit('vkuser/reset')
      this.$auth.clearToken()
      this.$root.$emit('authorization')
    },
    completeLogout: function () {
      this.loading = true
      console.debug('VK logout procedure...')
      this.$http
        .delete(this.$eps.logout)
        .then(resp => {
          if (resp.ok) {
            this.logout()
          }
        })
        .catch(this.$errorNotify)
        .finally(() => { this.loading = false })
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
  mounted () {
    if (this.is_authorized() && !this.user.id) this.reload()
  }
}
</script>

<style>
.bg-vk {
  background-color: #4680C2;
}
#proceed-btn {
  padding: 0 48px;
}
</style>
