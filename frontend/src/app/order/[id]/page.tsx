import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiError, getOrder } from "@/lib/api";
import { formatPrice } from "@/lib/format";

type Params = Promise<{ id: string }>;

export const metadata: Metadata = {
  title: "Order confirmed",
  robots: { index: false }, // order pages should not be indexed
};

export default async function OrderConfirmationPage({
  params,
}: {
  params: Params;
}) {
  const { id } = await params;

  let order;
  try {
    order = await getOrder(id);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  return (
    <main className="container-page py-16">
      <div className="mx-auto max-w-2xl">
        {/* Success header */}
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-3xl">
            ✓
          </div>
          <h1 className="mt-6 font-serif text-4xl font-bold text-espresso-900">
            Thank you, {order.customer_name.split(" ")[0]}!
          </h1>
          <p className="mt-3 text-espresso-600">
            Your order{" "}
            <span className="font-semibold text-espresso-900">#{order.id}</span>{" "}
            has been received. A confirmation was sent to{" "}
            <span className="font-medium">{order.customer_email}</span>.
          </p>
          <span className="mt-4 inline-flex items-center gap-2 rounded-full bg-gold-100 px-4 py-1.5 text-sm font-medium capitalize text-gold-700">
            Status: {order.status}
          </span>
        </div>

        {/* Order details */}
        <section className="mt-10 rounded-2xl bg-cream-50 p-6 shadow-card">
          <h2 className="font-serif text-xl font-semibold text-espresso-900">
            Order details
          </h2>
          <ul className="mt-4 divide-y divide-cream-200">
            {order.order_items.map((line) => (
              <li key={line.id} className="flex justify-between gap-3 py-3 text-sm">
                <span className="text-espresso-800">
                  {line.quantity} × {line.menu_item_name}
                  <span className="ml-2 text-espresso-400">
                    @ {formatPrice(line.unit_price)}
                  </span>
                </span>
                <span className="whitespace-nowrap font-medium text-espresso-900">
                  {formatPrice(line.subtotal)}
                </span>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex justify-between border-t border-cream-300 pt-4 text-lg font-semibold text-espresso-900">
            <span>Total</span>
            <span>{formatPrice(order.total_amount)}</span>
          </div>

          {(order.address || order.notes) && (
            <dl className="mt-6 space-y-3 border-t border-cream-200 pt-4 text-sm">
              {order.address && (
                <div>
                  <dt className="font-medium text-espresso-800">Delivery to</dt>
                  <dd className="text-espresso-600">{order.address}</dd>
                </div>
              )}
              {order.notes && (
                <div>
                  <dt className="font-medium text-espresso-800">Notes</dt>
                  <dd className="text-espresso-600">{order.notes}</dd>
                </div>
              )}
            </dl>
          )}
        </section>

        <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
          <Link href="/menu" className="btn-primary">
            Order something else
          </Link>
          <Link href="/" className="btn-secondary">
            Back home
          </Link>
        </div>
      </div>
    </main>
  );
}
