"use client";

import { useEffect } from "react";

/**
 * Global error boundary. Rendered when a route throws (e.g. the API is
 * unreachable). Error boundaries must be Client Components.
 */
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // In production this is where you'd forward to an error-tracking service.
    console.error(error);
  }, [error]);

  return (
    <main className="container-page flex min-h-[60vh] flex-col items-center justify-center py-24 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-cream-200 text-3xl">
        ⚠️
      </div>
      <h1 className="mt-6 font-serif text-3xl font-bold text-espresso-900">
        Something went wrong
      </h1>
      <p className="mt-3 max-w-md text-espresso-600">
        We couldn’t load this page. This can happen if the kitchen (our API) is
        temporarily unavailable. Please try again.
      </p>
      <button type="button" onClick={reset} className="btn-primary mt-8">
        Try again
      </button>
    </main>
  );
}
