"use client";

import { CartProvider } from "@/context/CartContext";

/** Client-side context providers shared across the app. */
export function Providers({ children }: { children: React.ReactNode }) {
  return <CartProvider>{children}</CartProvider>;
}
