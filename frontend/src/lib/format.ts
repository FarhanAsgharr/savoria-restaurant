/** Small presentation helpers shared across components. */

/** Format a decimal-string or number price as USD, e.g. "27" → "$27.00". */
export function formatPrice(value: string | number): string {
  const amount = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(amount)) return "$0.00";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}
