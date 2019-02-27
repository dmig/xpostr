import { Notify } from 'quasar'

export default ({ Vue }) => {
  Vue.prototype.$errorNotify = function (error) {
    Notify.create({
      message: error instanceof Error ? error.message : (error.statusText + ': ' + error.data.error),
      icon: 'error',
      color: 'negative'
    })
    if (process.env.NODE_ENV !== 'production') {
      console.error(error)
    }
  }
  Vue.errorNotify = Vue.prototype.$errorNotify
}
