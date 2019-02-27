import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'

import connections from './connections'
import sources from './sources'
import targets from './targets'
import vkuser from './vkuser'
import tguser from './tguser'

Vue.use(Vuex)

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation
 */

export default function (/* { ssrContext } */) {
  const Store = new Vuex.Store({
    plugins: [createPersistedState()],
    modules: {
      connections,
      sources,
      targets,
      vkuser,
      tguser
    }
  })

  if (module.hot) {
    module.hot.accept([
      './connections',
      './sources',
      './targets',
      './vkuser',
      './tguser'
    ], () => {
      Store.hotUpdate({
        modules: {
          connections: require('./connections').default,
          sources: require('./sources').default,
          targets: require('./targets').default,
          vkuser: require('./vkuser').default,
          tguser: require('./tguser').default
        }
      })
    })
  }

  return Store
}
