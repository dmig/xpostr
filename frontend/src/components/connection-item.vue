<template>
  <q-item>
    <q-item-section avatar>
      <q-btn flat round :disable="!source.uri" @click="goto('t.me', source.uri)" title="Open channel">
        <tg-avatar :size="$q.screen.gt.xs ? '32px' : '16px'" :src="source.photo" />
      </q-btn>
    </q-item-section>
    <q-item-section>
      <q-item-label class="row content-center">
        <div class="name-label ellipsis col-12 col-sm-5">{{source.title}}</div>
        <div class="name-label col-2 text-center gt-xs">&LongRightArrow;</div>
        <div class="name-label ellipsis col-12 col-sm-5 text-right">{{target.title}}</div>
      </q-item-label>
      <q-item-label :lines="1" caption v-if="item.last_status" class="text-blue-grey">
        <span v-if="item.last_update" class="text-grey">{{item.last_update | formatTime}}</span> {{item.last_status}}
      </q-item-label>
    </q-item-section>
    <q-item-section avatar>
      <q-btn flat round :disable="!target.uri"  @click="goto('vk.com', target.uri)" title="Open group">
        <q-avatar :size="$q.screen.gt.xs ? '32px' : '16px'">
          <img v-if="target.photo" :src="target.photo"/>
          <img v-else src="~assets/VK_Blue_Logo.svg"/>
        </q-avatar>
      </q-btn>
    </q-item-section>
    <q-item-section side>
      <confirm-button :size="$q.screen.gt.xs ? 'md' : 'sm'" round icon="delete" color="negative"
        @confirm="del(item)" title="Remove"/>
    </q-item-section>
    <q-item-section side>
      <q-btn :size="$q.screen.gt.xs ? 'md' : 'sm'" round color="primary"
        :icon="item.active ?'pause' : 'play_arrow'" :title="item.active ? 'Stop' : 'Start'"
        @click="toggle_state()" />
    </q-item-section>
  </q-item>
</template>

<script>
import ConfirmButton from 'components/confirm-button'
import TgAvatar from 'components/tg-avatar'
import { openURL } from 'quasar'

export default {
  name: 'ConnectionItem',
  components: { ConfirmButton, TgAvatar },
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
      let d = new Date(ts * 1000), now = new Date().getTime()
      if (Math.abs(now - ts * 1000) < 86400000) {
        return d.toLocaleTimeString(navigator.language)
      }
      return d.toLocaleString(navigator.language)
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
