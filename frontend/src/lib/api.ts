/**
 * Typed API client for the Django REST backend.
 *
 * A single `request` helper centralizes base-URL resolution, JSON parsing,
 * error handling and Next.js fetch caching. Feature helpers build on it so
 * components never construct URLs by hand (DRY).
 */

import type {
  Category,
  MenuItem,
  OrderConfirmation,
  OrderItemInput,
  Paginated,
} from "@/types";

// Browser → the site's own /api path, proxied to the backend by the route
// handler (app/api/[...path]). Same-origin everywhere: no CORS, no public
// backend URL, unaffected by any DNS blocking.
const BROWSER_API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";

// Server-side rendering talks to the backend directly. In production set
// BACKEND_ORIGIN (e.g. https://savoria-api.onrender.com); locally it defaults
// to the dev server.
const backendOrigin = process.env.BACKEND_ORIGIN;
const SERVER_API_URL =
  process.env.INTERNAL_API_URL ??
  (backendOrigin ? `${backendOrigin}/api` : "http://127.0.0.1:8000/api");

const API_URL =
  typeof window === "undefined" ? SERVER_API_URL : BROWSER_API_URL;

/** Thrown for any non-2xx API response so callers can render error states. */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface RequestOptions extends RequestInit {
  /** Next.js revalidation window in seconds (ISR). Defaults to 60s. */
  revalidate?: number;
}

async function request<T>(
  path: string,
  { revalidate = 60, ...init }: RequestOptions = {},
): Promise<T> {
  const url = `${API_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...init.headers },
    next: { revalidate },
    ...init,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      /* response had no JSON body */
    }
    throw new ApiError(`API ${res.status}: ${detail}`, res.status);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/** Loose shape accepted by the query-string builder. */
type QueryParams = Record<string, string | number | boolean | undefined>;

/** Build a query string from a params object, skipping empty values. */
function qs(params: QueryParams): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  const s = search.toString();
  return s ? `?${s}` : "";
}

// ── Categories ───────────────────────────────────────────────
export function getCategories(): Promise<Paginated<Category>> {
  return request<Paginated<Category>>("/categories/");
}

export function getCategory(slug: string): Promise<Category> {
  return request<Category>(`/categories/${slug}/`);
}

// ── Menu items ───────────────────────────────────────────────
export interface MenuItemQuery extends QueryParams {
  category?: string;
  search?: string;
  ordering?: string;
  is_available?: boolean;
  page?: number;
  page_size?: number;
}

export function getMenuItems(
  query: MenuItemQuery = {},
): Promise<Paginated<MenuItem>> {
  return request<Paginated<MenuItem>>(`/items/${qs(query)}`);
}

export function getMenuItem(slug: string): Promise<MenuItem> {
  return request<MenuItem>(`/items/${slug}/`);
}

export function getFeaturedItems(): Promise<Paginated<MenuItem>> {
  return request<Paginated<MenuItem>>(`/items/${qs({ is_featured: true })}`);
}

// ── Orders (used from Phase 2) ───────────────────────────────
export interface CreateOrderPayload {
  customer_name: string;
  customer_email: string;
  customer_phone?: string;
  address?: string;
  notes?: string;
  items: OrderItemInput[];
}

export function createOrder(
  payload: CreateOrderPayload,
): Promise<OrderConfirmation> {
  return request<OrderConfirmation>("/orders/", {
    method: "POST",
    body: JSON.stringify(payload),
    revalidate: 0, // never cache a mutation
  });
}

export function getOrder(id: number | string): Promise<OrderConfirmation> {
  return request<OrderConfirmation>(`/orders/${id}/`, { revalidate: 0 });
}
