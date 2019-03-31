const base = process.env.API

export const endpoints = {
  login: base + '/vkauth',
  vkuser: base + '/vkuser',
  tguser: base + '/tguser',
  tgauth: base + '/tgauth',
  sources: base + '/sources',
  targets: base + '/targets',
  connections: base + '/connections'
}

// leave the export, even if you don't use it
export default ({ Vue }) => {
  Vue.prototype.$eps = endpoints
  Vue.eps = endpoints
}
