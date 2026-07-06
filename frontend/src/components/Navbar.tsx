"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { CartButton } from "@/components/CartButton";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/menu", label: "Menu" },
  { href: "/#about", label: "Our Story" },
];

/** Responsive, accessible top navigation with a mobile drawer. */
export function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Subtle background shift once the user scrolls past the hero.
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Close the mobile menu whenever the route changes.
  useEffect(() => setOpen(false), [pathname]);

  return (
    <header
      className={`sticky top-0 z-50 transition-colors duration-300 ${
        scrolled
          ? "bg-cream-50/90 shadow-sm backdrop-blur"
          : "bg-transparent"
      }`}
    >
      <nav
        className="container-page flex h-16 items-center justify-between"
        aria-label="Primary"
      >
        <Link
          href="/"
          className="font-serif text-2xl font-bold tracking-tight text-espresso-900"
        >
          Savoria
        </Link>

        {/* Desktop links */}
        <ul className="hidden items-center gap-8 md:flex">
          {LINKS.map((link) => {
            const active =
              link.href === "/"
                ? pathname === "/"
                : pathname.startsWith(link.href.split("#")[0]) &&
                  link.href !== "/#about";
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className={`text-sm font-medium transition-colors hover:text-gold-600 ${
                    active ? "text-gold-600" : "text-espresso-800"
                  }`}
                >
                  {link.label}
                </Link>
              </li>
            );
          })}
          <li>
            <CartButton />
          </li>
        </ul>

        {/* Mobile: cart + toggle */}
        <div className="flex items-center gap-1 md:hidden">
          <CartButton />
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md p-2 text-espresso-900"
            aria-expanded={open}
            aria-controls="mobile-menu"
            aria-label="Toggle navigation menu"
            onClick={() => setOpen((v) => !v)}
          >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            {open ? (
              <path
                d="M6 6l12 12M6 18L18 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            ) : (
              <path
                d="M4 7h16M4 12h16M4 17h16"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            )}
          </svg>
          </button>
        </div>
      </nav>

      {/* Mobile drawer */}
      {open && (
        <div id="mobile-menu" className="border-t border-cream-300 bg-cream-50 md:hidden">
          <ul className="container-page flex flex-col gap-1 py-4">
            {LINKS.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="block rounded-lg px-3 py-2 text-espresso-800 hover:bg-cream-200"
                >
                  {link.label}
                </Link>
              </li>
            ))}
            <li className="mt-2 px-3">
              <Link href="/menu" className="btn-primary w-full text-sm">
                Order Now
              </Link>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}
