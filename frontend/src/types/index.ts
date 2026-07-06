/** Shared domain types mirroring the Django REST API responses. */

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  image: string | null;
  display_order: number;
  item_count: number;
}

export interface MenuItem {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: string; // DecimalField serializes as a string
  image: string | null;
  is_available: boolean;
  is_featured: boolean;
  category: number;
  category_name: string;
  category_slug: string;
}

/** Standard DRF page-number pagination envelope. */
export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/** A single line in the cart / an order (used from Phase 2 onward). */
export interface OrderItemInput {
  menu_item: number;
  quantity: number;
}
