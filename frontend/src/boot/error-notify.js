import { Notify } from 'quasar'

export default ({ Vue }) => {
  Vue.prototype.$errorNotify = function (error) {
    Notify.create({
      message: error instanceof Error ? error.message
        : error.status
          ? (error.data && error.data.error && error.data.data
            ? error.data.error + ': ' + error.data.data
            : error.statusText + ': ' + (error.data.error ? error.data.error : error.data))
          : 'Connection error',
      icon: 'error',
      color: 'negative'
    })
    if (process.env.NODE_ENV !== 'production') {
      console.error(error)
    }
  }
  Vue.errorNotify = Vue.prototype.$errorNotify
}
