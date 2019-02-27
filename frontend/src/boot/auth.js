const getToken = () => {
  return localStorage.getItem('token')
}

const getTokenPayload = () => {
  let ret = getToken()
  if (!ret) return {}

  ret = ret.substr(7).split('.')
  if (ret.length === 2 || ret.length === 3) { // Token with a valid JWT format XXX.YYY[.ZZZ]
    try { // Could be a valid JWT or an access token with the same format
      const base64 = ret[1].replace('-', '+').replace('_', '/')
      return JSON.parse(window.atob(base64))
    } catch (e) {
      return {} // Pass: Non-JWT token that looks like JWT
    }
  }
  return {}
}

export default ({ Vue, router }) => {
  if (!Vue.http) {
    throw new Error('Vue-resource plugin is required to use auth plugin')
  }

  const checkErrors = (response, request) => {
    // If token is expired, refresh, resubmit original request & resolve response for original request
    if (response.status === 401 || response.status === 403) {
      if (response.status === 401) clearToken()
      return Promise.reject(response)
    }
    // Otherwise just resolve the current response
    return Promise.resolve(response)
  }

  const clearToken = () => {
    delete Vue.http.headers.common['Authorization']
    return localStorage.removeItem('token')
  }

  const authInterceptor = (request, next) => {
    next(response => {
      // Check for expired token response, if expired, refresh token and resubmit original request
      if (response.headers.get('Authorization')) {
        const token = response.headers.get('Authorization')
        Vue.http.headers.common['Authorization'] = token
        localStorage.setItem('token', token)
      }
      return checkErrors(response, request)
    })
  }

  const token = getToken()
  if (token) {
    Vue.http.headers.common['Authorization'] = token
  }

  Vue.http.interceptors.push(authInterceptor)
  Vue.prototype.$auth = {
    getToken,
    getTokenPayload,
    clearToken
  }

  router.beforeEach((to, from, next) => {
    const auth = to.matched.reduce(
      (acc, record) => {
        if (!record.meta) return acc

        if (record.meta.requireAuth !== undefined) acc.requireAuth = record.meta.requireAuth
        if (record.meta.requireRole !== undefined) acc.role = record.meta.requireRole
        return acc
      },
      {}
    )
    if (!auth.requireAuth) return next()

    const user = getTokenPayload()
    if (user) {
      const roles = user.aud || ['guest']
      if (auth.role && !roles.includes(auth.role)) {
        return next({ path: '/403' })
      }
      return next()
    }
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  })
}
