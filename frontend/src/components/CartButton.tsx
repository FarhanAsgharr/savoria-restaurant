"use client";

import Link from "next/link";

import { useCart } from "@/context/CartContext";

/** Navbar cart link with a live item-count badge. */
export function CartButton() {
  const { totalQuantity, hydrated } = useCart();

  return (
    <Link
      href="/cart"
      aria-label={`Cart, ${totalQuantity} item${totalQuantity === 1 ? "" : "s"}`}
      className="relative inline-flex items-center justify-center rounded-full p-2 text-espresso-800 transition-colors hover:text-gold-600"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M6 6h15l-1.5 9h-12L5 3H2"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle cx="9" cy="20" r="1.5" fill="currentColor" />
        <circle cx="18" cy="20" r="1.5" fill="currentColor" />
      </svg>
      {hydrated && totalQuantity > 0 && (
        <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-gold-500 px-1 text-xs font-semibold text-white">
          {totalQuantity}
        </span>
      )}
    </Link>
  );
}
