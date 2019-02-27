export const fill = (state, data) => {
  reset(state)

  data && data.forEach(state.list.push)
}

export const reset = (state) => {
  state.list = []
}
