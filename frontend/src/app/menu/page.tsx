import type { Metadata } from "next";

import { CategoryFilter } from "@/components/CategoryFilter";
import { FoodCard } from "@/components/FoodCard";
import { EmptyState, SectionHeading } from "@/components/states";
import { SearchBar } from "@/components/SearchBar";
import { SortSelect } from "@/components/SortSelect";
import { getCategories, getMenuItems } from "@/lib/api";

export const metadata: Metadata = {
  title: "Menu",
  description:
    "Browse Savoria's full menu — starters, main courses, desserts and drinks. Search and filter by category.",
};

/** In Next 15, `searchParams` is a Promise and must be awaited. */
type SearchParams = Promise<{ category?: string; search?: string; ordering?: string }>;

export default async function MenuPage({ searchParams }: { searchParams: SearchParams }) {
  const { category, search, ordering } = await searchParams;

  const [categoriesRes, itemsRes] = await Promise.allSettled([
    getCategories(),
    getMenuItems({ category, search, ordering, page_size: 100 }),
  ]);

  const categories =
    categoriesRes.status === "fulfilled" ? categoriesRes.value.results : [];
  const items = itemsRes.status === "fulfilled" ? itemsRes.value.results : [];
  const total = itemsRes.status === "fulfilled" ? itemsRes.value.count : 0;

  return (
    <main className="container-page py-14">
      <SectionHeading
        eyebrow="The Menu"
        title="Every dish, one place"
        description="Filter by category or search for your favourite dish."
      />

      {/* Controls */}
      <div className="mt-8 flex flex-col gap-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <SearchBar />
          <SortSelect />
        </div>
        <CategoryFilter categories={categories} />
      </div>

      <p className="mt-6 text-sm text-espresso-600">
        {total} {total === 1 ? "dish" : "dishes"}
        {search ? ` matching “${search}”` : ""}
      </p>

      {/* Results */}
      <div className="mt-6">
        {items.length > 0 ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((item, i) => (
              <FoodCard key={item.id} item={item} index={i} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No dishes found"
            message="We couldn’t find any dishes matching your filters. Try clearing the search or picking another category."
            actionHref="/menu"
            actionLabel="Reset filters"
          />
        )}
      </div>
    </main>
  );
}
