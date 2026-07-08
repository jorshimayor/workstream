import { useEffect, useState, type DependencyList } from 'react'

export type AsyncState<T> =
  | { status: 'loading' }
  | { status: 'ok'; data: T }
  | { status: 'error'; error: unknown }

// Minimal async hook. No server-state cache library in this chunk; screen chunks
// can introduce one when a real screen needs caching. Pass `deps` (e.g. `[id]`)
// when the loader depends on changing inputs so it re-runs; defaults to load-once.
export function useAsync<T>(loader: () => Promise<T>, deps: DependencyList = []): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({ status: 'loading' })

  useEffect(() => {
    let active = true
    setState({ status: 'loading' })
    loader()
      .then((data) => {
        if (active) setState({ status: 'ok', data })
      })
      .catch((error: unknown) => {
        if (active) setState({ status: 'error', error })
      })
    return () => {
      active = false
    }
    // The caller owns the dependency contract via `deps`.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return state
}
