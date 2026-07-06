"use client";

import Link from "next/link";

import { DishImage } from "@/components/DishImage";
import { EmptyState, SectionHeading } from "@/components/states";
import { useCart } from "@/context/CartContext";
import { formatPrice } from "@/lib/format";

/** Shopping cart: review items, adjust quantities, proceed to checkout. */
export default function CartPage() {
  const { lines, hydrated, totalAmount, totalQuantity, setQuantity, removeItem } =
    useCart();

  // Avoid a flash of "empty cart" before localStorage hydrates.
  if (!hydrated) {
    return (
      <main className="container-page py-14">
        <div className="h-10 w-48 skeleton rounded" />
        <div className="mt-8 space-y-4">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-28 w-full skeleton rounded-2xl" />
          ))}
        </div>
      </main>
    );
  }

  if (lines.length === 0) {
    return (
      <main className="container-page py-14">
        <SectionHeading title="Your cart" />
        <div className="mt-8">
          <EmptyState
            title="Your cart is empty"
            message="Looks like you haven’t added anything yet. Explore our menu to find something delicious."
            actionHref="/menu"
            actionLabel="Browse the menu"
          />
        </div>
      </main>
    );
  }

  return (
    <main className="container-page py-14">
      <SectionHeading title="Your cart" description={`${totalQuantity} item${totalQuantity === 1 ? "" : "s"} ready to order.`} />

      <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_360px]">
        {/* Line items */}
        <ul className="space-y-4">
          {lines.map(({ product, quantity }) => (
            <li
              key={product.id}
              className="flex gap-4 rounded-2xl bg-cream-50 p-4 shadow-card"
            >
              <Link
                href={`/menu/${product.category_slug}/${product.slug}`}
                className="relative h-24 w-24 shrink-0 overflow-hidden rounded-xl"
              >
                <DishImage src={product.image} alt={product.name} sizes="96px" />
              </Link>

              <div className="flex flex-1 flex-col">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-gold-600">
                      {product.category_name}
                    </p>
                    <Link
                      href={`/menu/${product.category_slug}/${product.slug}`}
                      className="font-serif text-lg font-semibold text-espresso-900 hover:text-gold-700"
                    >
                      {product.name}
                    </Link>
                  </div>
                  <p className="whitespace-nowrap font-semibold text-espresso-900">
                    {formatPrice(parseFloat(product.price) * quantity)}
                  </p>
                </div>

                <div className="mt-auto flex items-center justify-between pt-3">
                  {/* Quantity stepper */}
                  <div className="inline-flex items-center rounded-full border border-cream-300">
                    <button
                      type="button"
                      onClick={() => setQuantity(product.id, quantity - 1)}
                      aria-label={`Decrease ${product.name} quantity`}
                      className="flex h-9 w-9 items-center justify-center rounded-full text-lg text-espresso-800 hover:text-gold-600"
                    >
                      −
                    </button>
                    <span className="w-8 text-center text-sm font-medium">
                      {quantity}
                    </span>
                    <button
                      type="button"
                      onClick={() => setQuantity(product.id, quantity + 1)}
                      aria-label={`Increase ${product.name} quantity`}
                      className="flex h-9 w-9 items-center justify-center rounded-full text-lg text-espresso-800 hover:text-gold-600"
                    >
                      +
                    </button>
                  </div>

                  <button
                    type="button"
                    onClick={() => removeItem(product.id)}
                    className="text-sm text-espresso-500 hover:text-red-600"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>

        {/* Order summary */}
        <aside className="h-fit rounded-2xl bg-espresso-900 p-6 text-cream-50 lg:sticky lg:top-24">
          <h2 className="font-serif text-xl font-semibold">Order summary</h2>
          <dl className="mt-4 space-y-2 text-sm text-cream-100/80">
            <div className="flex justify-between">
              <dt>Subtotal</dt>
              <dd>{formatPrice(totalAmount)}</dd>
            </div>
            <div className="flex justify-between">
              <dt>Estimated tax</dt>
              <dd>Calculated at checkout</dd>
            </div>
          </dl>
          <div className="mt-4 flex justify-between border-t border-cream-100/10 pt-4 text-lg font-semibold">
            <span>Total</span>
            <span>{formatPrice(totalAmount)}</span>
          </div>
          <Link
            href="/checkout"
            className="btn-primary mt-6 w-full"
          >
            Proceed to checkout
          </Link>
          <Link
            href="/menu"
            className="mt-3 block text-center text-sm text-cream-100/70 hover:text-gold-300"
          >
            Continue browsing
          </Link>
        </aside>
      </div>
    </main>
  );
}
