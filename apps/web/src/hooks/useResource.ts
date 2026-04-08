import { startTransition, useEffect, useState } from "react";

type ResourceState<T> = {
  data: T;
  loading: boolean;
  error: string | null;
};

export function useResource<T>(
  loader: () => Promise<T>,
  initialData: T,
  deps: readonly unknown[],
): ResourceState<T> {
  const [state, setState] = useState<ResourceState<T>>({
    data: initialData,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let active = true;
    setState({
      data: initialData,
      loading: true,
      error: null,
    });

    loader()
      .then((data) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setState({
            data,
            loading: false,
            error: null,
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
          });
        });
      });

    return () => {
      active = false;
    };
  }, deps);

  return state;
}
