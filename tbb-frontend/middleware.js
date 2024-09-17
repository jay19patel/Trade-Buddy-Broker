import { NextResponse } from 'next/server';

export function middleware(request) {

//   const token = request.cookies.get('access_token');
//   return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!login|register).*)',
  ],
};
