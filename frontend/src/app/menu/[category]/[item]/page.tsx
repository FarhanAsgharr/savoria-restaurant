import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { DishImage } from "@/components/DishImage";
import { FoodCard } from "@/components/FoodCard";
import { SectionHeading } from "@/components/states";
import { ApiError, getMenuItem, getMenuItems } from "@/lib/api";
import { formatPrice } from "@/lib/format";

type Params = Promise<{ category: string; item: string }>;

export async function generateStaticParams() {
  try {
    const { results } = await getMenuItems();
    return results.map((i) => ({ category: i.category_slug, item: i.slug }));
  } catch {
    return [];
  }
}

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const { item: slug } = await params;
  try {
    const item = await getMenuItem(slug);
    return {
      title: item.name,
      description: item.description || `${item.name} — available at Savoria.`,
      openGraph: item.image ? { images: [item.image] } : undefined,
    };
  } catch {
    return { title: "Dish" };
  }
}

export default async function ItemPage({ params }: { params: Params }) {
  const { item: slug } = await params;

  let item;
  try {
    item = await getMenuItem(slug);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  // Fetch a few related dishes from the same category.
  const relatedRes = await getMenuItems({ category: item.category_slug });
  const related = relatedRes.results.filter((i) => i.id !== item.id).slice(0, 3);

  return (
    <main className="container-page py-14">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="mb-6 text-sm text-espresso-400">
        <Link href="/menu" className="hover:text-gold-600">
          Menu
        </Link>
        <span className="mx-2">/</span>
        <Link
          href={`/menu/${item.category_slug}`}
          className="hover:text-gold-600"
        >
          {item.category_name}
        </Link>
        <span className="mx-2">/</span>
        <span className="text-espresso-800">{item.name}</span>
      </nav>

      <div className="grid gap-10 lg:grid-cols-2">
        {/* Image */}
        <div className="relative aspect-[4/3] overflow-hidden rounded-2xl shadow-card">
          <DishImage
            src={item.image}
            alt={item.name}
            sizes="(max-width: 1024px) 100vw, 50vw"
            priority
          />
        </div>

        {/* Details */}
        <div className="flex flex-col">
          <p className="text-sm font-medium uppercase tracking-wider text-gold-600">
            {item.category_name}
          </p>
          <h1 className="mt-2 font-serif text-4xl font-bold text-espresso-900">
            {item.name}
          </h1>
          <p className="mt-4 text-3xl font-semibold text-espresso-900">
            {formatPrice(item.price)}
          </p>

          <span
            className={`mt-4 inline-flex w-fit items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${
              item.is_available
                ? "bg-green-100 text-green-800"
                : "bg-espresso-100 text-espresso-600"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                item.is_available ? "bg-green-600" : "bg-espresso-400"
              }`}
            />
            {item.is_available ? "Available now" : "Currently unavailable"}
          </span>

          {item.description && (
            <p className="mt-6 leading-relaxed text-espresso-600">
              {item.description}
            </p>
          )}

          {/* Ordering (cart) is implemented in Phase 2. */}
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href={`/menu/${item.category_slug}`} className="btn-secondary">
              ← Back to {item.category_name}
            </Link>
          </div>
          <p className="mt-4 text-sm text-espresso-400">
            Online ordering launches in Phase 2.
          </p>
        </div>
      </div>

      {/* Related dishes */}
      {related.length > 0 && (
        <section className="mt-20">
          <SectionHeading eyebrow="You may also like" title="More from this menu" />
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {related.map((r) => (
              <FoodCard key={r.id} item={r} />
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
