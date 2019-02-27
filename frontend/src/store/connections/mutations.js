import Vue from 'vue'

const getKey = (item) => item.vk_id + '-' + item.tg_id

export const fill = (state, data) => {
  reset(state)

  data && data.forEach(el => {
    Vue.set(state.index, getKey(el), el)
    state.list.push(el)
  })
}

export const reset = (state) => {
  state.index = {}
  state.list = []
}

export const set = (state, item) => {
  let k = getKey(item)

  if (state.index[k]) {
    Vue.set(state.index[k], 'active', item.active)
    return
  }

  Vue.set(state.index, k, item)
  state.list.push(item)
}

export const del = (state, item) => {
  let k = getKey(item), el = state.index[k]

  if (!el) return

  let ix = state.list.indexOf(el)
  Vue.delete(state.index, k)
  Vue.delete(state.list, ix)
}
