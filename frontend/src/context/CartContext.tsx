"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import type { CartLine, CartProduct } from "@/types";

const STORAGE_KEY = "savoria_cart_v1";
const MAX_QTY = 100;

interface CartContextValue {
  lines: CartLine[];
  /** True once the cart has been hydrated from localStorage (client only). */
  hydrated: boolean;
  totalQuantity: number;
  totalAmount: number;
  addItem: (product: CartProduct, quantity?: number) => void;
  setQuantity: (productId: number, quantity: number) => void;
  removeItem: (productId: number) => void;
  clear: () => void;
}

const CartContext = createContext<CartContextValue | null>(null);

function clampQty(qty: number): number {
  return Math.max(1, Math.min(MAX_QTY, Math.floor(qty)));
}

/**
 * Provides cart state to the whole app and persists it to localStorage,
 * so the cart survives reloads and is shared across tabs.
 */
export function CartProvider({ children }: { children: React.ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([]);
  const [hydrated, setHydrated] = useState(false);

  // Hydrate from localStorage on mount (client only → avoids SSR mismatch).
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setLines(JSON.parse(raw) as CartLine[]);
    } catch {
      /* corrupt storage → start empty */
    }
    setHydrated(true);
  }, []);

  // Persist on every change (after hydration).
  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(lines));
  }, [lines, hydrated]);

  // Keep multiple tabs in sync.
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && e.newValue) {
        try {
          setLines(JSON.parse(e.newValue) as CartLine[]);
        } catch {
          /* ignore */
        }
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const addItem = useCallback((product: CartProduct, quantity = 1) => {
    setLines((prev) => {
      const existing = prev.find((l) => l.product.id === product.id);
      if (existing) {
        return prev.map((l) =>
          l.product.id === product.id
            ? { ...l, quantity: clampQty(l.quantity + quantity) }
            : l,
        );
      }
      return [...prev, { product, quantity: clampQty(quantity) }];
    });
  }, []);

  const setQuantity = useCallback((productId: number, quantity: number) => {
    setLines((prev) =>
      prev.map((l) =>
        l.product.id === productId ? { ...l, quantity: clampQty(quantity) } : l,
      ),
    );
  }, []);

  const removeItem = useCallback((productId: number) => {
    setLines((prev) => prev.filter((l) => l.product.id !== productId));
  }, []);

  const clear = useCallback(() => setLines([]), []);

  const totalQuantity = useMemo(
    () => lines.reduce((sum, l) => sum + l.quantity, 0),
    [lines],
  );

  const totalAmount = useMemo(
    () => lines.reduce((sum, l) => sum + parseFloat(l.product.price) * l.quantity, 0),
    [lines],
  );

  const value = useMemo(
    () => ({
      lines,
      hydrated,
      totalQuantity,
      totalAmount,
      addItem,
      setQuantity,
      removeItem,
      clear,
    }),
    [
      lines,
      hydrated,
      totalQuantity,
      totalAmount,
      addItem,
      setQuantity,
      removeItem,
      clear,
    ],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

/** Access the cart. Must be used within a <CartProvider>. */
export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within a CartProvider");
  return ctx;
}
