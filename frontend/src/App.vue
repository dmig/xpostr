<template>
  <div id="q-app" style="max-width: 950px; margin: auto">
    <vk-card class="q-ma-sm"></vk-card>
    <tg-card class="q-ma-sm" v-if="is_auth"></tg-card>
    <connect-groups-card class="q-ma-sm" v-if="is_tg_authorized"></connect-groups-card>
    <create-dialog v-if="is_tg_authorized"></create-dialog>
  </div>
</template>

<style>
</style>

<script>
import AuthMixin from 'components/auth-mixin'
import VkCard from 'components/vk-card'
import TgCard from 'components/tg-card'
import ConnectGroupsCard from 'components/connect-groups-card'
import CreateDialog from 'components/create-dialog'

export default {
  name: 'App',
  mixins: [AuthMixin],
  components: { VkCard, TgCard, ConnectGroupsCard, CreateDialog },
  computed: {
    is_vk_authorized () {
      return this.$store.state.vkuser.id !== 0
    },
    is_tg_authorized () {
      return this.$store.state.tguser.authorized
    }
  },
  data () {
    return {
      is_auth: false
    }
  },
  mounted () {
    this.is_auth = this.is_authorized()
    this.$root.$on('authorization', () => {
      this.is_auth = this.is_authorized()
    })
  }
}
</script>
