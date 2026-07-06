/**
 * Same-origin API proxy.
 *
 * The browser calls the site's own `/api/*` path; this handler forwards the
 * request server-side to the Django backend — preserving the trailing slash
 * DRF requires. This means the browser never talks to the backend directly:
 * no CORS, no public backend URL, and it works unchanged behind a tunnel or
 * on any network (including ones that block the backend's public domain).
 */
import { NextRequest, NextResponse } from "next/server";

const BACKEND_ORIGIN = process.env.BACKEND_ORIGIN ?? "http://127.0.0.1:8000";

// Hop-by-hop headers that must not be forwarded.
const STRIP = new Set([
  "host",
  "connection",
  "content-length",
  "accept-encoding",
  "transfer-encoding",
]);

async function proxy(req: NextRequest): Promise<NextResponse> {
  // Rebuild the target URL, keeping the exact path (with trailing slash) + query.
  const { pathname, search } = req.nextUrl;
  const target = `${BACKEND_ORIGIN}${pathname}${search}`;

  const headers = new Headers();
  req.headers.forEach((value, key) => {
    if (!STRIP.has(key.toLowerCase())) headers.set(key, value);
  });

  const method = req.method;
  const body =
    method === "GET" || method === "HEAD" ? undefined : await req.arrayBuffer();

  const res = await fetch(target, {
    method,
    headers,
    body,
    redirect: "manual",
    cache: "no-store",
  });

  // Stream the backend response back to the browser.
  const resHeaders = new Headers(res.headers);
  resHeaders.delete("content-encoding");
  resHeaders.delete("transfer-encoding");

  return new NextResponse(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers: resHeaders,
  });
}

export {
  proxy as GET,
  proxy as POST,
  proxy as PUT,
  proxy as PATCH,
  proxy as DELETE,
  proxy as OPTIONS,
};
