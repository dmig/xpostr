<template>
  <q-card>
    <q-list :class="{'q-py-md': true, 'q-px-md': $q.screen.gt.xs}">
      <q-item :dense="$q.screen.xs">
        <q-item-section>
          <q-item-label class="text-subtitle1">
            Telegram channel &#10140; VK group<span v-if="$q.screen.gt.xs"> connections</span>
          </q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn flat round :loading="loading" icon="refresh" @click="reload" title="Refresh"/>
        </q-item-section>
      </q-item>
    </q-list>
    <q-list :class="{'q-pb-md': true, 'q-px-md': $q.screen.gt.xs}">
      <q-list separator>
        <connection-item :item="item" v-for="item in connections" :key="item.tg_id + '-' + item.vk_id"/>
      </q-list>
    </q-list>

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
</style>
