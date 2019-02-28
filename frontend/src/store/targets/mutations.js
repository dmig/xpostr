import Vue from 'vue'

export const fill = (state, data) => {
  reset(state)

  data && data.forEach(el => {
    Vue.set(state.index, el.id, el)
    state.list.push(el)
  })
}

export const reset = (state) => {
  Vue.set(state, 'index', {})
  Vue.set(state, 'list', [])
}
