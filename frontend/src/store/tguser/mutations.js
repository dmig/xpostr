export function fill (state, user) {
  reset(state)
  if (!user) return
  for (let k in state) state[k] = user[k]
}

export function reset (state) {
  state.authorized = false
  state.fullname = ''
  state.username = ''
  state.photo = null
}
