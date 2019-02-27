<template>
  <q-page padding>
    <vk-card class="q-mb-md"></vk-card>
    <tg-card class="q-mb-md" v-if="is_authorized()"></tg-card>
    <connect-groups-card v-if="is_tg_authorized"></connect-groups-card>
    <create-dialog v-if="is_tg_authorized"></create-dialog>
  </q-page>
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
  name: 'PageIndex',
  mixins: [AuthMixin],
  components: { VkCard, TgCard, ConnectGroupsCard, CreateDialog },
  computed: {
    is_vk_authorized () {
      return this.$store.state.vkuser.id !== 0
    },
    is_tg_authorized () {
      return this.$store.state.tguser.authorized
    }
  }
}
</script>
