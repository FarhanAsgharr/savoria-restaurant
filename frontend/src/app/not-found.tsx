import Link from "next/link";

/** Global 404 page. */
export default function NotFound() {
  return (
    <main className="container-page flex min-h-[60vh] flex-col items-center justify-center py-24 text-center">
      <p className="font-serif text-7xl font-bold text-gold-500">404</p>
      <h1 className="mt-4 font-serif text-3xl font-bold text-espresso-900">
        Page not found
      </h1>
      <p className="mt-3 max-w-md text-espresso-600">
        The page you’re looking for doesn’t exist or may have been moved. Let’s get you
        back to something delicious.
      </p>
      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <Link href="/" className="btn-primary">
          Back home
        </Link>
        <Link href="/menu" className="btn-secondary">
          Browse the menu
        </Link>
      </div>
    </main>
  );
}
