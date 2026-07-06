import Link from "next/link";

import { DishImage } from "@/components/DishImage";
import type { Category } from "@/types";

/** A clickable category tile linking to that category's menu section. */
export function CategoryCard({ category }: { category: Category }) {
  return (
    <Link
      href={`/menu/${category.slug}`}
      className="group relative block aspect-[3/4] overflow-hidden rounded-2xl shadow-card focus:outline-none focus-visible:ring-2 focus-visible:ring-gold-500 focus-visible:ring-offset-2"
    >
      <DishImage
        src={category.image}
        alt={category.name}
        sizes="(max-width: 640px) 50vw, 25vw"
        className="transition-transform duration-500 group-hover:scale-105"
      />
      {/* Legibility gradient over the image. */}
      <div className="absolute inset-0 bg-gradient-to-t from-espresso-900/85 via-espresso-900/20 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 p-5 text-cream-50">
        <h3 className="font-serif text-2xl font-semibold">{category.name}</h3>
        <p className="mt-1 text-sm text-cream-100/80">
          {category.item_count} {category.item_count === 1 ? "dish" : "dishes"}
        </p>
      </div>
    </Link>
  );
}
