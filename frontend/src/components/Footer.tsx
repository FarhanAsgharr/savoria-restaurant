import Link from "next/link";

/** Site footer with contact details, hours and navigation. */
export function Footer() {
  const year = 2026;
  return (
    <footer className="mt-20 bg-espresso-900 text-cream-100">
      <div className="container-page grid gap-10 py-14 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <p className="font-serif text-2xl font-bold text-cream-50">Savoria</p>
          <p className="mt-3 max-w-xs text-sm text-cream-100/70">
            Seasonal, chef-crafted dishes made from the finest local ingredients.
          </p>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gold-300">
            Explore
          </h3>
          <ul className="mt-4 space-y-2 text-sm text-cream-100/80">
            <li>
              <Link href="/" className="hover:text-gold-300">
                Home
              </Link>
            </li>
            <li>
              <Link href="/menu" className="hover:text-gold-300">
                Menu
              </Link>
            </li>
            <li>
              <Link href="/#about" className="hover:text-gold-300">
                Our Story
              </Link>
            </li>
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gold-300">
            Visit Us
          </h3>
          <address className="mt-4 space-y-2 text-sm not-italic text-cream-100/80">
            <p>128 Vineyard Avenue</p>
            <p>Napa, CA 94558</p>
            <p>
              <a href="tel:+17075550142" className="hover:text-gold-300">
                (707) 555-0142
              </a>
            </p>
          </address>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gold-300">
            Hours
          </h3>
          <ul className="mt-4 space-y-2 text-sm text-cream-100/80">
            <li>Tue – Thu · 5pm – 10pm</li>
            <li>Fri – Sat · 5pm – 11pm</li>
            <li>Sun · 4pm – 9pm</li>
            <li>Mon · Closed</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-cream-100/10 py-6 text-center text-xs text-cream-100/50">
        © {year} Savoria. All rights reserved.
      </div>
    </footer>
  );
}
