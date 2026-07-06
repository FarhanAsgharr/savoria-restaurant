import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { FoodCard } from "@/components/FoodCard";
import { EmptyState, SectionHeading } from "@/components/states";
import { ApiError, getCategories, getCategory, getMenuItems } from "@/lib/api";

type Params = Promise<{ category: string }>;

/** Pre-render a page for each category at build time. */
export async function generateStaticParams() {
  try {
    const { results } = await getCategories();
    return results.map((c) => ({ category: c.slug }));
  } catch {
    return [];
  }
}

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const { category: slug } = await params;
  try {
    const category = await getCategory(slug);
    return {
      title: category.name,
      description:
        category.description || `Explore our ${category.name} at Savoria.`,
    };
  } catch {
    return { title: "Category" };
  }
}

export default async function CategoryPage({ params }: { params: Params }) {
  const { category: slug } = await params;

  let category;
  try {
    category = await getCategory(slug);
  } catch (err) {
    // A missing category should render the 404 page, not a server error.
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  const itemsRes = await getMenuItems({ category: slug, page_size: 100 });
  const items = itemsRes.results;

  return (
    <main className="container-page py-14">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="mb-6 text-sm text-espresso-400">
        <Link href="/menu" className="hover:text-gold-600">
          Menu
        </Link>
        <span className="mx-2">/</span>
        <span className="text-espresso-800">{category.name}</span>
      </nav>

      <SectionHeading
        eyebrow="Category"
        title={category.name}
        description={category.description || undefined}
      />

      <div className="mt-10">
        {items.length > 0 ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((item) => (
              <FoodCard key={item.id} item={item} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No dishes in this category yet"
            message="Please check back soon — our chefs are working on it."
            actionHref="/menu"
            actionLabel="Back to full menu"
          />
        )}
      </div>
    </main>
  );
}
