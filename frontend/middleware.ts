/**
 * Middleware
 * Route protection and authentication
 * Note: Token stored in localStorage, checked client-side in layout
 */

import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Token is stored in localStorage (client-side only)
  // Middleware can't access localStorage, so we allow all routes and check in layout/page level
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
