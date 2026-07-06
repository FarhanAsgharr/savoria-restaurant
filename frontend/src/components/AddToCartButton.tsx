"use client";

import { useState } from "react";

import { useCart } from "@/context/CartContext";
import type { CartProduct } from "@/types";

interface Props {
  product: CartProduct;
  available?: boolean;
  variant?: "full" | "compact";
}

/**
 * Adds a product to the cart.
 * - `full`    → quantity stepper + primary button (item detail page)
 * - `compact` → single button (menu cards)
 * Shows brief "Added ✓" feedback after each add.
 */
export function AddToCartButton({
  product,
  available = true,
  variant = "compact",
}: Props) {
  const { addItem } = useCart();
  const [quantity, setQuantity] = useState(1);
  const [justAdded, setJustAdded] = useState(false);

  const handleAdd = () => {
    if (!available) return;
    addItem(product, variant === "full" ? quantity : 1);
    setJustAdded(true);
    setQuantity(1);
    window.setTimeout(() => setJustAdded(false), 1600);
  };

  if (!available) {
    return (
      <button
        type="button"
        disabled
        className="inline-flex cursor-not-allowed items-center justify-center rounded-full bg-espresso-100 px-6 py-3 font-medium text-espresso-400"
      >
        Unavailable
      </button>
    );
  }

  if (variant === "compact") {
    return (
      <button
        type="button"
        onClick={handleAdd}
        aria-label={`Add ${product.name} to cart`}
        className="btn-primary !px-4 !py-2 text-sm"
      >
        {justAdded ? "Added ✓" : "Add to cart"}
      </button>
    );
  }

  // Full variant: quantity stepper + add button.
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
      <div
        className="inline-flex items-center rounded-full border border-cream-300 bg-cream-50"
        role="group"
        aria-label="Quantity"
      >
        <button
          type="button"
          onClick={() => setQuantity((q) => Math.max(1, q - 1))}
          aria-label="Decrease quantity"
          className="flex h-11 w-11 items-center justify-center rounded-full text-xl text-espresso-800 hover:text-gold-600"
        >
          −
        </button>
        <span aria-live="polite" className="w-8 text-center font-medium">
          {quantity}
        </span>
        <button
          type="button"
          onClick={() => setQuantity((q) => Math.min(100, q + 1))}
          aria-label="Increase quantity"
          className="flex h-11 w-11 items-center justify-center rounded-full text-xl text-espresso-800 hover:text-gold-600"
        >
          +
        </button>
      </div>

      <button
        type="button"
        onClick={handleAdd}
        className="btn-primary flex-1 sm:flex-none"
      >
        {justAdded ? "Added to cart ✓" : "Add to cart"}
      </button>
    </div>
  );
}
