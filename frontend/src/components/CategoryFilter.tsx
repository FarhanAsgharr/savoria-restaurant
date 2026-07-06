"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { Category } from "@/types";

/**
 * Horizontal, scrollable category filter chips for the menu page.
 * Selecting a chip sets ?category=<slug> while preserving the search term.
 */
export function CategoryFilter({ categories }: { categories: Category[] }) {
  const params = useSearchParams();
  const active = params.get("category") ?? "";

  const hrefFor = (slug: string) => {
    const next = new URLSearchParams(params.toString());
    if (slug) next.set("category", slug);
    else next.delete("category");
    const s = next.toString();
    return s ? `?${s}` : "?";
  };

  const chip = (slug: string, label: string) => {
    const selected = active === slug;
    return (
      <Link
        key={slug || "all"}
        href={hrefFor(slug)}
        scroll={false}
        aria-current={selected ? "true" : undefined}
        className={`whitespace-nowrap rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
          selected
            ? "border-gold-500 bg-gold-500 text-white"
            : "border-cream-300 bg-cream-50 text-espresso-800 hover:border-gold-400 hover:text-gold-700"
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {chip("", "All")}
      {categories.map((c) => chip(c.slug, c.name))}
    </div>
  );
}
