export function fill (state, user) {
  reset(state)
  if (!user) return
  for (let k in state) if (k in user) state[k] = user[k]
}

export function reset (state) {
  state.id = 0
  state.fullname = ''
  state.photo = null
}
