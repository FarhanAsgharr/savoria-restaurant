import Link from "next/link";

/** Reusable presentational states: empty results, section headings, skeletons. */

export function SectionHeading({
  eyebrow,
  title,
  description,
  center = false,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  center?: boolean;
}) {
  return (
    <div className={center ? "mx-auto max-w-2xl text-center" : "max-w-2xl"}>
      {eyebrow && (
        <p className="text-sm font-medium uppercase tracking-[0.25em] text-gold-600">
          {eyebrow}
        </p>
      )}
      <h2 className="mt-2 font-serif text-3xl font-bold text-espresso-900 sm:text-4xl">
        {title}
      </h2>
      {description && <p className="mt-3 text-espresso-600">{description}</p>}
    </div>
  );
}

export function EmptyState({
  title = "Nothing here yet",
  message = "We couldn’t find anything to show. Try adjusting your search.",
  actionHref,
  actionLabel,
}: {
  title?: string;
  message?: string;
  actionHref?: string;
  actionLabel?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-cream-300 bg-cream-50 px-6 py-16 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-cream-200 text-2xl">
        🍽️
      </div>
      <h3 className="mt-4 font-serif text-xl font-semibold text-espresso-900">
        {title}
      </h3>
      <p className="mt-2 max-w-sm text-sm text-espresso-600">{message}</p>
      {actionHref && actionLabel && (
        <Link href={actionHref} className="btn-secondary mt-6 text-sm">
          {actionLabel}
        </Link>
      )}
    </div>
  );
}

/** A single shimmering placeholder card matching the FoodCard layout. */
export function FoodCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl bg-cream-50 shadow-card">
      <div className="skeleton aspect-[4/3] w-full" />
      <div className="space-y-3 p-5">
        <div className="skeleton h-3 w-20 rounded" />
        <div className="skeleton h-5 w-3/4 rounded" />
        <div className="skeleton h-4 w-full rounded" />
        <div className="skeleton h-4 w-2/3 rounded" />
      </div>
    </div>
  );
}

/** A responsive grid of skeleton cards for loading states. */
export function FoodGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <FoodCardSkeleton key={i} />
      ))}
    </div>
  );
}
