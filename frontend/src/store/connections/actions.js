import Vue from 'vue'

export function set ({ commit }, item) {
  return Vue.http.post(Vue.eps.connections, item)
    .then(resp => {
      if (!resp.ok) return false
      commit('set', item)
      return true
    })
    .catch(Vue.errorNotify)
}

export function del ({ commit }, item) {
  return Vue.http.delete(Vue.eps.connections, { params: item })
    .then(resp => {
      if (!resp.ok) return false
      commit('del', item)
      return true
    })
    .catch(Vue.errorNotify)
}
