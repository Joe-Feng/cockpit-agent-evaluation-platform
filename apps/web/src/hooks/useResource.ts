import { startTransition, useEffect, useRef, useState } from "react";

type ResourceState<T> = {
  data: T;
  loading: boolean;
  error: string | null;
  refresh: () => void;
};

export function useResource<T>(
  loader: () => Promise<T>,
  initialData: T,
  deps: readonly unknown[],
): ResourceState<T> {
  const [refreshToken, setRefreshToken] = useState(0);
  const loaderRef = useRef(loader);
  const [state, setState] = useState<ResourceState<T>>({
    data: initialData,
    loading: true,
    error: null,
    refresh: () => setRefreshToken((token) => token + 1),
  });

  loaderRef.current = loader;

  useEffect(() => {
    let active = true;
    const refresh = () => setRefreshToken((token) => token + 1);
    setState({
      data: initialData,
      loading: true,
      error: null,
      refresh,
    });

    loaderRef.current()
      .then((data) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setState({
            data,
            loading: false,
            error: null,
            refresh,
          });
        });
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }
        const message = error instanceof Error ? error.message : "Request failed";
        startTransition(() => {
          setState({
            data: initialData,
            loading: false,
            error: message,
            refresh,
          });
        });
      });

    return () => {
      active = false;
    };
  }, [initialData, refreshToken, ...deps]);

  return state;
}
