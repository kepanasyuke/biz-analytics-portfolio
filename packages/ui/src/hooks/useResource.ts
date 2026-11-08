import { useEffect, useState } from 'react'

export type Resource<T> = { data: T | null; error: string | null; loading: boolean }

const readJson = <T,>(response: Response): Promise<T> =>
  response.ok ? (response.json() as Promise<T>) : Promise.reject(new Error(`${response.status} ${response.statusText}`))

const load = <T,>(url: string, set: (next: Resource<T>) => void): void => {
  fetch(url)
    .then((response) => readJson<T>(response))
    .then((data) => set({ data, error: null, loading: false }))
    .catch((error: Error) => set({ data: null, error: error.message, loading: false }))
}

const useLoader = <T,>(url: string, set: (next: Resource<T>) => void): void => {
  useEffect(() => load(url, set), [url, set])
}

export function useResource<T>(url: string): Resource<T> {
  const [state, setState] = useState<Resource<T>>({ data: null, error: null, loading: true })
  useLoader(url, setState)
  return state
}
