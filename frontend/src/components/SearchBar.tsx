"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

/**
 * Debounced search input that syncs the query to the URL (?search=...),
 * so results are shareable, bookmarkable and server-rendered.
 */
export function SearchBar({ placeholder = "Search dishes…" }: { placeholder?: string }) {
  const router = useRouter();
  const params = useSearchParams();
  const [value, setValue] = useState(params.get("search") ?? "");
  const first = useRef(true);

  useEffect(() => {
    // Skip the effect on initial mount to avoid a redundant navigation.
    if (first.current) {
      first.current = false;
      return;
    }
    const handle = setTimeout(() => {
      const next = new URLSearchParams(params.toString());
      if (value) next.set("search", value);
      else next.delete("search");
      router.replace(`?${next.toString()}`, { scroll: false });
    }, 350);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return (
    <div className="relative w-full max-w-md">
      <svg
        className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-espresso-400"
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
        <path d="M20 20l-3.5-3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        aria-label="Search the menu"
        className="w-full rounded-full border border-cream-300 bg-cream-50 py-3 pl-11 pr-4 text-espresso-900 placeholder:text-espresso-400 focus:border-gold-500 focus:outline-none focus:ring-2 focus:ring-gold-500/30"
      />
    </div>
  );
}
