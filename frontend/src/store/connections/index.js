import { extend } from 'quasar'

import baseState from '../base_state'
import * as baseGetters from '../base_getters'
import * as baseMutations from '../base_mutations'
import BaseActions from '../base_actions'

import state from './state'
import * as getters from './getters'
import * as mutations from './mutations'
import * as actions from './actions'

import { endpoints } from '../../boot/endpoints'

export default {
  namespaced: true,
  state: extend(true, {}, baseState, state),
  getters: extend({}, baseGetters, getters),
  mutations: extend({}, baseMutations, mutations),
  actions: extend({}, new BaseActions(endpoints.connections), actions)
}
