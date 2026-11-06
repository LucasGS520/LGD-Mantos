import { useCallback, useEffect, useRef, useState } from "react";

/** Mantém a última carga válida e descarta respostas de telas/filtros antigos. */
export function useData<T>(fetcher: () => Promise<T>, key: unknown = null) {
  const fetcherRef = useRef(fetcher);
  const [revision, setRevision] = useState(0);
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    fetcherRef.current = fetcher;
  });
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    Promise.resolve()
      .then(() => fetcherRef.current())
      .then(
        (value) => {
          if (active) setData(value);
        },
        (cause) => {
          if (active)
            setError(
              cause instanceof Error ? cause.message : "Erro ao carregar",
            );
        },
      )
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [key, revision]);
  const reload = useCallback(() => setRevision((value) => value + 1), []);
  return { data, loading, error, reload };
}
