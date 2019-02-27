<template>
  <q-card bordered>
    <q-card-section>
      <q-item dense>
        <q-item-section>
          <q-item-label class="text-subtitle1">
            Telegram channel &LongRightArrow; VK Group connections
          </q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn flat round :loading="loading" icon="refresh" @click="reload" title="Refresh"/>
        </q-item-section>
      </q-item>
    </q-card-section>
    <q-card-section>
      <q-list separator dense v-show="!loading">
        <q-item v-for="item in connections" :key="item.tg_id + '-' + item.vk_id">
          <q-item-section avatar>
            <q-avatar size="32px">
              <img v-if="sources[item.tg_id].photo" :src="sources[item.tg_id].photo" />
              <img v-else src="~assets/Telegram_logo.svg" />
            </q-avatar>
          </q-item-section>
          <q-item-section>
            <q-item-label class="row content-center">
              <div class="col-5 name-label">{{sources[item.tg_id].title}}</div>
              <div class="col-2 name-label text-center">&LongRightArrow;</div>
              <div class="col-5 name-label text-right">{{targets[item.vk_id].title}}</div>
            </q-item-label>
            <q-item-label caption v-if="item.last_status" class="text-blue-grey"><span v-if="item.last_update" class="text-grey">{{item.last_update | formatTime}}</span> {{item.last_status}}</q-item-label>
          </q-item-section>
          <q-item-section avatar>
            <q-avatar size="32px">
              <img v-if="targets[item.vk_id].photo" :src="targets[item.vk_id].photo" />
              <img v-else src="~assets/VK_Blue_Logo.svg" />
            </q-avatar>
          </q-item-section>
          <q-item-section side>
            <confirm-button round icon="delete" color="negative" @confirm="del(item)" title="Remove"/>
          </q-item-section>
          <q-item-section side>
            <q-btn round color="primary" v-show="!item.active" icon="play_arrow" @click="toggle_state(item)" title="Start"/>
            <q-btn round color="primary" v-show="item.active" icon="pause" @click="toggle_state(item)" title="Stop"/>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>

    <q-separator />

    <q-card-actions align="right">
      <q-btn color="primary" icon-right="add" stretch @click="$root.$emit('openDialog')">Create new</q-btn>
    </q-card-actions>
  </q-card>
</template>

<script>
import ConfirmButton from 'components/confirm-button'

export default {
  // name: 'ComponentName',
  components: { ConfirmButton },
  data () {
    return {
      loading: false
    }
  },
  computed: {
    connections () {
      return this.$store.state.connections.list
        .filter(item => this.sources[item.tg_id] && this.targets[item.vk_id])
    },
    sources () {
      return this.$store.state.sources.index
    },
    targets () {
      return this.$store.state.targets.index
    }
  },
  methods: {
    formatTime (ts) {
      return (new Date(ts * 1000)).toLocaleString(navigator.language)
    },
    del (item) {
      console.debug('Delete connection', item.vk_id, item.tg_id)
      let payload = {
        vk_id: item.vk_id,
        tg_id: item.tg_id
      }
      this.$store.dispatch('connections/del', payload)
    },
    add (item) {
      let payload = {
        vk_id: item.vk_id,
        tg_id: item.tg_id,
        active: item.active
      }
      console.debug('Add connection', payload.vk_id, payload.tg_id, payload.active)
      this.$store.dispatch('connections/set', payload)
    },
    toggle_state (item) {
      let payload = {
        vk_id: item.vk_id,
        tg_id: item.tg_id
      }
      payload.active = !item.active
      console.debug('Set connection state', payload.vk_id, payload.tg_id, payload.active)
      this.$store.dispatch('connections/set', payload)
    },
    reload () {
      this.loading = true
      this.$store.dispatch('connections/load').finally(() => { this.loading = false })
    }
  },
  mounted () {
    if (!this.connections) this.reload()
    this.$root.$on('createConnection', this.add)
  }
}
</script>

<style scoped>
.name-label {
  height: 1.2em
}
</style>
