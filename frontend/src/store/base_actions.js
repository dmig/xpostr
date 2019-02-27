import Vue from 'vue'

export default function (endpoint) {
  const load = ({ commit }) => {
    console.info('Requesting', endpoint)
    return Vue.http.get(endpoint)
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

  return { load }
}
