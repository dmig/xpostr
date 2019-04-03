<template>
  <q-avatar :size="size">
    <img v-if="source" :src="source" @error="tryLater"/>
    <img v-else src="~assets/Telegram_logo.svg"/>
  </q-avatar>
</template>

<script>
export default {
  name: 'TgAvatar',
  props: {
    size: String,
    src: String
  },
  data () {
    return {
      source: null,
      try: 0,
      timer: null
    }
  },
  methods: {
    tryLater () {
      console.debug('Error loading avatar from', this.src)

      this.source = null
      if (this.try > 2) {
        console.debug('Giving up...')
        return
      }
      this.try++

      self.timer = setTimeout(() => {
        this.source = this.src
      }, 3000)
    }
  },
  created () {
    this.source = this.src
  }
}
</script>

<style>
</style>
