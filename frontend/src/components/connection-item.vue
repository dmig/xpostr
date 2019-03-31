<template>
  <q-item :item="item">
    <q-item-section avatar>
      <q-btn round :disable="!source.uri" @click="goto('t.me', source.uri)" title="Open channel">
        <q-avatar size="32px">
          <img v-if="source.photo" :src="source.photo"/>
          <img v-else src="~assets/Telegram_logo.svg"/>
        </q-avatar>
      </q-btn>
    </q-item-section>
    <q-item-section>
      <q-item-label class="row content-center">
        <div class="name-label ellipsis col-12 col-sm-5">{{source.title}}</div>
        <div class="name-label col-2 text-center gt-xs">&LongRightArrow;</div>
        <div class="name-label ellipsis col-12 col-sm-5 text-right">{{target.title}}</div>
      </q-item-label>
      <q-item-label caption v-if="item.last_status" class="text-blue-grey">
        <span v-if="item.last_update" class="text-grey">{{item.last_update | formatTime}}</span> {{item.last_status}}
      </q-item-label>
    </q-item-section>
    <q-item-section avatar>
      <q-btn round :disable="!target.uri"  @click="goto('vk.com', target.uri)" title="Open group">
        <q-avatar size="32px">
          <img v-if="target.photo" :src="target.photo"/>
          <img v-else src="~assets/VK_Blue_Logo.svg"/>
        </q-avatar>
      </q-btn>
    </q-item-section>
    <q-item-section side>
      <confirm-button round icon="delete" color="negative" @confirm="del(item)" title="Remove"/>
    </q-item-section>
    <q-item-section side>
      <q-btn round color="primary" v-show="!item.active" icon="play_arrow" @click="toggle_state()" title="Start"/>
      <q-btn round color="primary" v-show="item.active" icon="pause" @click="toggle_state()" title="Stop"/>
    </q-item-section>
  </q-item>
</template>

<script>
import ConfirmButton from 'components/confirm-button'
import { openURL } from 'quasar'

export default {
  name: 'ConnectionItem',
  components: { ConfirmButton },
  props: {
    item: Object
  },
  computed: {
    source () {
      return this.item && this.$store.state.sources.index[this.item.tg_id]
        ? this.$store.state.sources.index[this.item.tg_id]
        : { id: this.item.tg_id, title: 'Unknown channel (' + this.item.tg_id + ')' }
    },
    target () {
      return this.item && this.$store.state.targets.index[this.item.vk_id]
        ? this.$store.state.targets.index[this.item.vk_id]
        : { id: this.item.vk_id, title: 'Unknown group (' + this.item.vk_id + ')' }
    }
  },
  data () {
    return {

    }
  },
  filters: {
    formatTime (ts) {
      return (new Date(ts * 1000)).toLocaleString(navigator.language)
    }
  },
  methods: {
    del () {
      console.debug('Delete connection', this.item.vk_id, this.item.tg_id)
      let payload = {
        vk_id: this.item.vk_id,
        tg_id: this.item.tg_id
      }
      this.$store.dispatch('connections/del', payload)
    },
    toggle_state () {
      let payload = {
        vk_id: this.item.vk_id,
        tg_id: this.item.tg_id,
        active: !this.item.active
      }
      console.debug('Set connection state', payload.vk_id, payload.tg_id, payload.active)
      this.$store.dispatch('connections/set', payload)
    },
    goto (dest, uri) {
      if (!uri) return

      openURL('https://' + dest + '/' + uri)
    }
  }
}
</script>

<style>
</style>
