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
      <q-list separator v-show="!loading">
        <connection-item :item="item" v-for="item in connections" :key="item.tg_id + '-' + item.vk_id"/>
      </q-list>
    </q-card-section>

    <q-separator />

    <q-card-actions align="right">
      <q-btn color="primary" icon-right="add" stretch @click="$root.$emit('openDialog')">Create new</q-btn>
    </q-card-actions>
  </q-card>
</template>

<script>
import ConnectionItem from 'components/connection-item'

export default {
  // name: 'ComponentName',
  components: { ConnectionItem },
  data () {
    return {
      loading: false
    }
  },
  computed: {
    connections () {
      return this.$store.state.connections.list
    }
  },
  methods: {
    add (item) {
      let payload = {
        vk_id: item.vk_id,
        tg_id: item.tg_id,
        active: item.active
      }
      console.debug('Add connection', payload.vk_id, payload.tg_id, payload.active)
      this.$store.dispatch('connections/set', payload)
    },
    reload () {
      this.loading = true
      this.$store.dispatch('connections/load').finally(() => { this.loading = false })
    }
  },
  mounted () {
    if (!this.connections.length) this.reload()
    this.$root.$on('createConnection', this.add)
  }
}
</script>

<style>
.name-label {
  height: 1.2em !important
}
</style>
