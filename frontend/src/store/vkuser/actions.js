import Vue from 'vue'

export function load ({ commit }) {
  return Vue.http.get(Vue.eps.vkuser)
    .then(resp => {
      if (!resp.ok) return false
      commit('fill', resp.data)
      return true
    })
    .catch(err => {
      Vue.errorNotify(err)
      commit('fill')
    })
}
