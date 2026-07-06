import Link from "next/link";

/**
 * Home page (Phase 0 foundation).
 *
 * A minimal but real landing hero that validates the design system
 * (fonts, colors, buttons, animations). The full Home experience —
 * featured categories, signature dishes and testimonials — is built
 * in Phase 1.
 */
export default function HomePage() {
  return (
    <main className="flex flex-1 items-center justify-center px-6 py-24">
      <section className="max-w-2xl text-center">
        <p className="mb-4 animate-fade-in-up text-sm font-medium uppercase tracking-[0.3em] text-gold-600">
          Fine Dining · Est. 2026
        </p>
        <h1 className="animate-fade-in-up font-serif text-5xl font-bold leading-tight text-espresso-900 sm:text-6xl">
          Savoria
        </h1>
        <p className="mx-auto mt-6 max-w-xl animate-fade-in-up text-lg text-espresso-600">
          Seasonal, chef-crafted dishes made from the finest local ingredients.
          A refined dining experience — now available to explore and order online.
        </p>
        <div className="mt-10 flex animate-fade-in-up flex-col items-center justify-center gap-4 sm:flex-row">
          <Link href="/menu" className="btn-primary">
            Explore the Menu
          </Link>
          <Link href="/#about" className="btn-secondary">
            Our Story
          </Link>
        </div>
      </section>
    </main>
  );
}
