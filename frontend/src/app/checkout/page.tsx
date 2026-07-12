"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useState } from "react";

import type { PickedLocation } from "@/components/AddressMap";
import { EmptyState, SectionHeading } from "@/components/states";
import { useCart } from "@/context/CartContext";
import { ApiError, createOrder } from "@/lib/api";
import { formatPrice } from "@/lib/format";

// Leaflet needs the browser, so load the map client-side only.
const AddressMap = dynamic(() => import("@/components/AddressMap"), {
  ssr: false,
  loading: () => (
    <div className="skeleton h-[340px] w-full rounded-xl" aria-label="Loading map" />
  ),
});

interface FormState {
  customer_name: string;
  customer_phone: string;
  address: string;
  notes: string;
}

const EMPTY_FORM: FormState = {
  customer_name: "",
  customer_phone: "",
  address: "",
  notes: "",
};

// Requires at least 7 digits (allowing +, spaces, dashes, parentheses).
const PHONE_RE = /^[+\d][\d\s()-]{6,}$/;

export default function CheckoutPage() {
  const router = useRouter();
  const { lines, hydrated, totalAmount, totalQuantity, clear } = useCart();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [coords, setCoords] = useState<{ latitude: number; longitude: number } | null>(
    null,
  );
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleMapChange = (loc: PickedLocation) => {
    setForm((f) => ({ ...f, address: loc.address }));
    setCoords({ latitude: loc.latitude, longitude: loc.longitude });
    setErrors((prev) => ({ ...prev, address: undefined }));
  };

  const update =
    (field: keyof FormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setForm((f) => ({ ...f, [field]: e.target.value }));
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    };

  const validate = (): boolean => {
    const next: Partial<Record<keyof FormState, string>> = {};
    if (!form.customer_name.trim()) next.customer_name = "Please enter your name.";
    if (!form.customer_phone.trim())
      next.customer_phone = "Please enter your phone number.";
    else if (!PHONE_RE.test(form.customer_phone.trim()))
      next.customer_phone = "Please enter a valid phone number.";
    if (!form.address.trim()) next.address = "Please enter your delivery address.";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    if (!validate()) return;

    setSubmitting(true);
    try {
      const order = await createOrder({
        customer_name: form.customer_name.trim(),
        customer_phone: form.customer_phone.trim(),
        address: form.address.trim(),
        latitude: coords?.latitude,
        longitude: coords?.longitude,
        notes: form.notes.trim() || undefined,
        items: lines.map((l) => ({
          menu_item: l.product.id,
          quantity: l.quantity,
        })),
      });
      clear();
      router.push(`/order/${order.id}`);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? "We couldn’t place your order. Please review your details and try again."
          : "Something went wrong. Please check your connection and try again.";
      setSubmitError(message);
      setSubmitting(false);
    }
  };

  if (!hydrated) {
    return (
      <main className="container-page py-14">
        <div className="skeleton h-10 w-48 rounded" />
        <div className="skeleton mt-8 h-96 w-full rounded-2xl" />
      </main>
    );
  }

  if (lines.length === 0) {
    return (
      <main className="container-page py-14">
        <SectionHeading title="Checkout" />
        <div className="mt-8">
          <EmptyState
            title="Your cart is empty"
            message="Add a few dishes before heading to checkout."
            actionHref="/menu"
            actionLabel="Browse the menu"
          />
        </div>
      </main>
    );
  }

  return (
    <main className="container-page py-14">
      <SectionHeading
        title="Checkout"
        description="Just a few details and your order is on its way."
      />

      <form
        onSubmit={handleSubmit}
        noValidate
        className="mt-10 grid gap-10 lg:grid-cols-[1fr_360px]"
      >
        {/* Customer details */}
        <div className="space-y-5">
          <Field
            id="customer_name"
            label="Full name"
            required
            value={form.customer_name}
            onChange={update("customer_name")}
            error={errors.customer_name}
            autoComplete="name"
          />
          <Field
            id="customer_phone"
            label="Phone number"
            type="tel"
            required
            value={form.customer_phone}
            onChange={update("customer_phone")}
            error={errors.customer_phone}
            autoComplete="tel"
          />
          {/* Address: type it directly, or use the map to auto-fill it. */}
          <div>
            <label htmlFor="address" className="text-sm font-medium text-espresso-800">
              Delivery address <span className="text-red-500">*</span>
            </label>
            <p className="text-espresso-500 mb-2 mt-0.5 text-xs">
              Type your address below, or search / drop a pin on the map to auto-fill it.
            </p>
            <AddressMap onChange={handleMapChange} />
            <textarea
              id="address"
              value={form.address}
              onChange={update("address")}
              rows={2}
              placeholder="Your full delivery address"
              autoComplete="street-address"
              aria-invalid={!!errors.address}
              className={`mt-3 w-full rounded-xl border bg-cream-50 px-4 py-3 text-espresso-900 placeholder:text-espresso-400 focus:outline-none focus:ring-2 focus:ring-gold-500/30 ${
                errors.address
                  ? "border-red-400"
                  : "border-cream-300 focus:border-gold-500"
              }`}
            />
            {errors.address && (
              <p className="mt-1 text-sm text-red-600">{errors.address}</p>
            )}
          </div>
          <Field
            id="notes"
            label="Special requests (optional)"
            value={form.notes}
            onChange={update("notes")}
            textarea
          />

          {submitError && (
            <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {submitError}
            </p>
          )}
        </div>

        {/* Order summary */}
        <aside className="h-fit rounded-2xl bg-espresso-900 p-6 text-cream-50 lg:sticky lg:top-24">
          <h2 className="font-serif text-xl font-semibold">
            Your order ({totalQuantity})
          </h2>
          <ul className="mt-4 space-y-3 text-sm">
            {lines.map(({ product, quantity }) => (
              <li
                key={product.id}
                className="flex justify-between gap-3 text-cream-100/80"
              >
                <span>
                  {quantity} × {product.name}
                </span>
                <span className="whitespace-nowrap">
                  {formatPrice(parseFloat(product.price) * quantity)}
                </span>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex justify-between border-t border-cream-100/10 pt-4 text-lg font-semibold">
            <span>Total</span>
            <span>{formatPrice(totalAmount)}</span>
          </div>

          <button type="submit" disabled={submitting} className="btn-primary mt-6 w-full">
            {submitting ? "Placing order…" : "Place order"}
          </button>
          <Link
            href="/cart"
            className="mt-3 block text-center text-sm text-cream-100/70 hover:text-gold-300"
          >
            Back to cart
          </Link>
        </aside>
      </form>
    </main>
  );
}

/** Accessible labelled input / textarea with inline error messaging. */
function Field({
  id,
  label,
  value,
  onChange,
  error,
  type = "text",
  required = false,
  textarea = false,
  autoComplete,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  error?: string;
  type?: string;
  required?: boolean;
  textarea?: boolean;
  autoComplete?: string;
}) {
  const base =
    "mt-1 w-full rounded-xl border bg-cream-50 px-4 py-3 text-espresso-900 placeholder:text-espresso-400 focus:outline-none focus:ring-2 focus:ring-gold-500/30";
  const borderClass = error ? "border-red-400" : "border-cream-300 focus:border-gold-500";

  return (
    <div>
      <label htmlFor={id} className="text-sm font-medium text-espresso-800">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {textarea ? (
        <textarea
          id={id}
          value={value}
          onChange={onChange}
          rows={3}
          autoComplete={autoComplete}
          className={`${base} ${borderClass}`}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
        />
      ) : (
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          required={required}
          autoComplete={autoComplete}
          className={`${base} ${borderClass}`}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
        />
      )}
      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
