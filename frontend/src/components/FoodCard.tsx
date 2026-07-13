import Link from "next/link";

import { AddToCartButton } from "@/components/AddToCartButton";
import { DishImage } from "@/components/DishImage";
import { formatPrice } from "@/lib/format";
import type { MenuItem } from "@/types";

/**
 * The signature menu-item card: image, category, name, description,
 * price and an availability badge. Links to the item detail page.
 */
export function FoodCard({ item, index = 0 }: { item: MenuItem; index?: number }) {
  const href = `/menu/${item.category_slug}/${item.slug}`;

  return (
    <article
      style={{ animationDelay: `${(index % 12) * 70}ms` }}
      className="group animate-fade-in-up overflow-hidden rounded-2xl bg-cream-50 shadow-card transition-all duration-300 hover:-translate-y-1.5 hover:shadow-card-hover"
    >
      <Link href={href} className="block focus:outline-none">
        <div className="relative aspect-[4/3] overflow-hidden">
          <DishImage
            src={item.image}
            alt={item.name}
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            className="transition-transform duration-500 group-hover:scale-105"
          />
          {!item.is_available && (
            <span className="absolute left-3 top-3 rounded-full bg-espresso-900/90 px-3 py-1 text-xs font-medium text-cream-50">
              Sold out
            </span>
          )}
          {item.is_featured && item.is_available && (
            <span className="absolute left-3 top-3 rounded-full bg-gold-500 px-3 py-1 text-xs font-medium text-white">
              Chef’s pick
            </span>
          )}
        </div>

        <div className="p-5 pb-3">
          <p className="text-xs font-medium uppercase tracking-wider text-gold-600">
            {item.category_name}
          </p>
          <div className="mt-1 flex items-start justify-between gap-3">
            <h3 className="font-serif text-xl font-semibold text-espresso-900 group-hover:text-gold-700">
              {item.name}
            </h3>
            <span className="whitespace-nowrap font-semibold text-espresso-900">
              {formatPrice(item.price)}
            </span>
          </div>
          <p className="mt-2 line-clamp-2 text-sm text-espresso-600">
            {item.description}
          </p>
        </div>
      </Link>

      {/* Quick-add sits outside the Link so it doesn't trigger navigation. */}
      <div className="flex items-center justify-end px-5 pb-5">
        <AddToCartButton
          product={{
            id: item.id,
            name: item.name,
            slug: item.slug,
            price: item.price,
            image: item.image,
            category_slug: item.category_slug,
            category_name: item.category_name,
          }}
          available={item.is_available}
          variant="compact"
        />
      </div>
    </article>
  );
}
