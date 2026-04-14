import { useState } from "react";

export function useAsyncAction<TArgs extends unknown[], TResult>(
  action: (...args: TArgs) => Promise<TResult>,
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(...args: TArgs): Promise<TResult> {
    setLoading(true);
    setError(null);

    try {
      return await action(...args);
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : "请求失败";
      setError(message);
      throw caught;
    } finally {
      setLoading(false);
    }
  }

  return { loading, error, run };
}
