<template>
  <q-btn
    :size="size" :title="title" :loading="loading"
    :round="round" :rounded="rounded" :outline="outline" :glossy="glossy"
    :push="push" :noCaps="noCaps" :disable="disable"
    :flat="!second_click" :color="color" @click="click">
    <q-icon v-if="icon" :name="icon" :class="{ 'on-left' : _label }" />{{ _label }}
  </q-btn>
</template>

<script>
export default {
  name: 'ConfirmButton',
  props: {
    disable: Boolean,
    glossy: Boolean,
    color: String,
    icon: String,
    label: String,
    loading: Boolean,
    noCaps: Boolean,
    outline: Boolean,
    push: Boolean,
    round: Boolean,
    rounded: Boolean,
    size: String,
    title: String
  },
  data () {
    return {
      second_click: false,
      timer: null
    }
  },
  computed: {
    _label () {
      return this.label ? this.label + (this.second_click ? '?' : '') : null
    }
  },
  methods: {
    reset () {
      this.second_click = false
      clearTimeout(this.timer)
    },
    click (e) {
      if (!this.second_click) {
        this.second_click = true
        this.timer = setTimeout(() => this.reset(), 3000)
        return
      }
      this.reset()
      this.$emit('confirm', e, () => {
        this.$emit('input', false)
      })
    }
  }
}
</script>

<style>
</style>
