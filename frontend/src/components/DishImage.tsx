import Image from "next/image";

/**
 * Renders an optimized dish/category image, or an elegant branded
 * fallback when no image is available. Reused by cards and detail pages.
 */
export function DishImage({
  src,
  alt,
  sizes,
  priority = false,
  className = "",
}: {
  src: string | null;
  alt: string;
  sizes?: string;
  priority?: boolean;
  className?: string;
}) {
  if (!src) {
    return (
      <div
        className={`flex items-center justify-center bg-gradient-to-br from-espresso-600 to-espresso-900 ${className}`}
        aria-label={`${alt} (image coming soon)`}
        role="img"
      >
        <span className="font-serif text-4xl text-gold-300/80">S</span>
      </div>
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      fill
      sizes={sizes ?? "(max-width: 768px) 100vw, 33vw"}
      priority={priority}
      className={`object-cover ${className}`}
    />
  );
}
