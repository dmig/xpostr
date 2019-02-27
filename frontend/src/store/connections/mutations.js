import Vue from 'vue'

export const fill = (state, data) => {
  reset(state)

  data && data.forEach(el => {
    state.list.push(el)
  })
}

export const reset = (state) => {
  state.list = []
}

export const set = (state, item) => {
  let k = state.list.findIndex(el => el.vk_id === item.vk_id && el.tg_id === item.tg_id)

  if (k === -1) state.list.push(item)
  else Vue.set(state.list[k], 'active', item.active)
}

export const del = (state, item) => {
  let k = state.list.findIndex(el => el.vk_id === item.vk_id && el.tg_id === item.tg_id)

  if (k === -1) return

  Vue.delete(state.list, k)
}
