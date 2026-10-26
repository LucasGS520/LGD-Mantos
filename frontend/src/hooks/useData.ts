import { useState, useEffect, useCallback } from 'react'

export function useData<T>(fetcher: () => Promise<T>, key: unknown = null) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setData(await fetcher())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao carregar')
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])

  useEffect(() => { load() }, [load])

  return { data, loading, error, reload: load }
}
