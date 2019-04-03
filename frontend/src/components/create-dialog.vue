<template>
  <q-dialog v-model="dialog">
    <q-card style="max-height: 80vh; max-width: 80vw; width: 60vw">
      <q-card-section>
        <div class="text-subtitile1">Create a connection</div>
      </q-card-section>

      <q-separator />

      <q-card-section style="height: 50vh">
        <q-select use-input outlined emit-value map-options
          input-debounce="100" option-value="id" option-label="title" class="q-mb-md"
          v-model="tg_id" :options="srcOpts" @filter="filterSrc" label="Telegram channel">
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps" v-on="scope.itemEvents">
              <q-item-section avatar>
                <q-avatar size="32px">
                  <img v-if="scope.opt.photo" :src="scope.opt.photo" />
                  <img v-else src="~assets/Telegram_logo.svg" />
                </q-avatar>
              </q-item-section>
              <q-item-section>
                <q-item-label>{{scope.opt.title}}</q-item-label>
              </q-item-section>
            </q-item>
          </template>
          <template v-slot:no-option>
            <q-item>
              <q-item-section>
                Nothing available
              </q-item-section>
            </q-item>
          </template>
        </q-select>
        <q-select use-input outlined emit-value map-options
          input-debounce="100" option-value="id" option-label="title" class="q-mb-md"
          v-model="vk_id" :options="tgtOpts" @filter="filterTgt" label="VK Group">
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps" v-on="scope.itemEvents">
              <q-item-section avatar>
                <q-avatar size="32px">
                  <img v-if="scope.opt.photo" :src="scope.opt.photo" />
                  <img v-else src="~assets/VK_Blue_Logo.svg" />
                </q-avatar>
              </q-item-section>
              <q-item-section>
                <q-item-label>{{scope.opt.title}}</q-item-label>
              </q-item-section>
            </q-item>
          </template>
          <template v-slot:no-option>
            <q-item>
              <q-item-section>
                Nothing available
              </q-item-section>
            </q-item>
          </template>
        </q-select>
        <q-checkbox v-model="active" label="Active" />
      </q-card-section>

      <q-separator />

      <q-card-actions align="right">
        <q-btn id="cancel-btn" label="Cancel" @click="reset"/>
        <q-btn id="create-btn" label="Create" color="primary" @click="submit"
          :disable="!vk_id || !tg_id"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
export default {
  // name: 'ComponentName',
  data () {
    return {
      dialog: false,
      srcOpts: [],
      tgtOpts: [],
      vk_id: '',
      tg_id: '',
      active: true
    }
  },
  computed: {
    sources () {
      return this.$store.state.sources.list
    },
    targets () {
      return this.$store.state.targets.list
    }
  },
  methods: {
    reset () {
      this.vk_id = ''
      this.tg_id = ''
      this.active = true
      this.dialog = false
    },
    submit () {
      if (!this.vk_id || !this.tg_id) return

      console.debug('emitting event createConnection')
      this.$root.$emit('createConnection', { vk_id: this.vk_id, tg_id: this.tg_id, active: this.active })
      this.reset()
    },
    filterSrc (val, update) {
      if (val === '') {
        update(() => {
          this.srcOpts = this.sources
        })
        return
      }

      update(() => {
        const needle = val.toLowerCase()
        this.srcOpts = this.sources.filter(v => v.title.toLowerCase().indexOf(needle) > -1)
      })
    },
    filterTgt (val, update) {
      if (val === '') {
        update(() => {
          this.tgtOpts = this.targets
        })
        return
      }

      update(() => {
        const needle = val.toLowerCase()
        this.tgtOpts = this.targets.filter(v => v.title.toLowerCase().indexOf(needle) > -1)
      })
    }
  },
  mounted () {
    this.$root.$on('openDialog', () => {
      this.dialog = true
    })
    this.srcOpts = this.sources
    this.tgtOpts = this.targets
  }
}
</script>

<style>
#create-btn, #cancel-btn {
  padding: 0 48px
}
</style>
