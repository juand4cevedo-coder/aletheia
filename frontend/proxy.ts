import { NextResponse, type NextRequest } from "next/server";

import {
  ACCESS_COOKIE,
  REFRESH_COOKIE,
  accessCookieOptions,
  refreshCookieOptions,
} from "@/lib/auth/cookies";
import { refreshTokens } from "@/lib/auth/refresh";

function toLogin(request: NextRequest) {
  const url = new URL("/login", request.url);
  url.searchParams.set("next", request.nextUrl.pathname);
  const response = NextResponse.redirect(url);
  response.cookies.delete(ACCESS_COOKIE);
  response.cookies.delete(REFRESH_COOKIE);
  return response;
}

/**
 * Mantiene viva la sesión en el área privada.
 *
 * Si la cookie de acceso ya caducó pero queda la de refresh, renueva los
 * tokens antes de renderizar. Es solo una comprobación optimista: cada página
 * y cada Server Action vuelven a verificar la sesión con la API.
 */
export async function proxy(request: NextRequest) {
  if (request.cookies.has(ACCESS_COOKIE)) {
    return NextResponse.next();
  }

  const refreshToken = request.cookies.get(REFRESH_COOKIE)?.value;
  if (!refreshToken) {
    return toLogin(request);
  }

  const pair = await refreshTokens(refreshToken);
  if (!pair) {
    return toLogin(request);
  }

  // La página que se renderiza ahora debe ver los tokens nuevos...
  request.cookies.set(ACCESS_COOKIE, pair.access_token);
  request.cookies.set(REFRESH_COOKIE, pair.refresh_token);
  const response = NextResponse.next({ request: { headers: request.headers } });

  // ...y el navegador debe guardarlos para las siguientes.
  response.cookies.set(ACCESS_COOKIE, pair.access_token, accessCookieOptions(pair.expires_in));
  response.cookies.set(REFRESH_COOKIE, pair.refresh_token, refreshCookieOptions());
  return response;
}

export const config = {
  matcher: ["/app/:path*"],
};