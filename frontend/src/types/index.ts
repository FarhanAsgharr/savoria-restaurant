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

/** The subset of a MenuItem we persist in the cart (localStorage). */
export type CartProduct = Pick<
  MenuItem,
  "id" | "name" | "slug" | "price" | "image" | "category_slug" | "category_name"
>;

/** A cart line: a product plus its chosen quantity. */
export interface CartLine {
  product: CartProduct;
  quantity: number;
}

/** Read shape of an order returned by GET /api/orders/<id>/. */
export interface OrderConfirmation {
  id: number;
  customer_name: string;
  customer_phone: string;
  address: string;
  notes: string;
  status: string;
  total_amount: string;
  created_at: string;
  order_items: {
    id: number;
    menu_item: number;
    menu_item_name: string;
    quantity: number;
    unit_price: string;
    subtotal: string;
  }[];
}
