export function set (state) {
  state.ts = Date.now()
}

export function reset (state) {
  state.ts = null
}
