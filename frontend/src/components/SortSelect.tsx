"use client";

import { useRouter, useSearchParams } from "next/navigation";

const OPTIONS = [
  { value: "", label: "Featured" },
  { value: "price", label: "Price: Low to High" },
  { value: "-price", label: "Price: High to Low" },
  { value: "name", label: "Name: A → Z" },
];

/** Sort control that syncs the chosen ordering to the URL (?ordering=). */
export function SortSelect() {
  const router = useRouter();
  const params = useSearchParams();
  const current = params.get("ordering") ?? "";

  const onChange = (value: string) => {
    const next = new URLSearchParams(params.toString());
    if (value) next.set("ordering", value);
    else next.delete("ordering");
    router.replace(`?${next.toString()}`, { scroll: false });
  };

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="sort" className="text-espresso-500 whitespace-nowrap text-sm">
        Sort by
      </label>
      <select
        id="sort"
        value={current}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-full border border-cream-300 bg-cream-50 py-2 pl-4 pr-8 text-sm text-espresso-900 focus:border-gold-500 focus:outline-none focus:ring-2 focus:ring-gold-500/30"
      >
        {OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}
