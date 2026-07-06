import Link from "next/link";

import { CategoryCard } from "@/components/CategoryCard";
import { FoodCard } from "@/components/FoodCard";
import { SectionHeading } from "@/components/states";
import { getCategories, getFeaturedItems } from "@/lib/api";

/**
 * Home page — the storefront's front door.
 *
 * Server-rendered: fetches categories and featured dishes at request time
 * (ISR-cached). Sections: hero → featured dishes → categories → our story.
 */
export default async function HomePage() {
  // Fetch in parallel; degrade gracefully if the API is unreachable.
  const [categoriesRes, featuredRes] = await Promise.allSettled([
    getCategories(),
    getFeaturedItems(),
  ]);

  const categories =
    categoriesRes.status === "fulfilled" ? categoriesRes.value.results : [];
  const featured =
    featuredRes.status === "fulfilled" ? featuredRes.value.results : [];

  return (
    <main>
      {/* ── Hero ────────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-espresso-900 text-cream-50">
        <div className="absolute inset-0 bg-gradient-to-br from-espresso-800 via-espresso-900 to-black" />
        <div className="absolute -right-24 -top-24 h-96 w-96 rounded-full bg-gold-500/10 blur-3xl" />
        <div className="container-page relative flex min-h-[78vh] flex-col items-start justify-center py-24">
          <p className="animate-fade-in-up text-sm font-medium uppercase tracking-[0.3em] text-gold-300">
            Fine Dining · Est. 2026
          </p>
          <h1 className="mt-4 max-w-3xl animate-fade-in-up font-serif text-5xl font-bold leading-tight sm:text-6xl lg:text-7xl">
            A taste of the <span className="text-gold-400">extraordinary</span>
          </h1>
          <p className="mt-6 max-w-xl animate-fade-in-up text-lg text-cream-100/80">
            Seasonal, chef-crafted dishes made from the finest local ingredients.
            Explore our menu and reserve your table for an unforgettable evening.
          </p>
          <div className="mt-10 flex animate-fade-in-up flex-col gap-4 sm:flex-row">
            <Link href="/menu" className="btn-primary">
              Explore the Menu
            </Link>
            <Link href="/#about" className="btn-secondary !border-cream-100/40 !text-cream-50 hover:!bg-cream-50 hover:!text-espresso-900">
              Our Story
            </Link>
          </div>
        </div>
      </section>

      {/* ── Featured dishes ─────────────────────────────────── */}
      {featured.length > 0 && (
        <section className="container-page py-20">
          <SectionHeading
            eyebrow="Chef’s Selection"
            title="Signature dishes"
            description="A handpicked selection of our most beloved plates."
          />
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {featured.slice(0, 6).map((item) => (
              <FoodCard key={item.id} item={item} />
            ))}
          </div>
        </section>
      )}

      {/* ── Categories ──────────────────────────────────────── */}
      {categories.length > 0 && (
        <section className="bg-cream-200/60 py-20">
          <div className="container-page">
            <SectionHeading
              eyebrow="The Menu"
              title="Explore by category"
              description="From delicate starters to indulgent desserts."
            />
            <div className="mt-10 grid grid-cols-2 gap-4 sm:gap-6 lg:grid-cols-4">
              {categories.map((category) => (
                <CategoryCard key={category.id} category={category} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── Our Story ───────────────────────────────────────── */}
      <section id="about" className="container-page scroll-mt-20 py-24">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="Our Story"
              title="Rooted in craft & community"
            />
            <div className="mt-6 space-y-4 text-espresso-600">
              <p>
                Savoria began with a simple belief: that a great meal is more than
                food — it’s a moment shared. Since 2026, our kitchen has celebrated
                the seasons, partnering with local farms and growers to bring the
                freshest ingredients to your table.
              </p>
              <p>
                Every dish is composed with intention by our culinary team, balancing
                classic technique with a spirit of discovery. Whether it’s an intimate
                dinner or a special celebration, we’re honoured to be part of your story.
              </p>
            </div>
            <Link href="/menu" className="btn-primary mt-8">
              View the full menu
            </Link>
          </div>
          <div className="relative aspect-[4/3] overflow-hidden rounded-2xl bg-gradient-to-br from-gold-300 via-gold-500 to-espresso-800 shadow-card">
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="font-serif text-7xl font-bold text-cream-50/90">
                Savoria
              </span>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
