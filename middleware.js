import { NextResponse } from 'next/server'
const publicRoutes = ['/login', '/registration', '/hello-world',"/accounts","/tickets"]

export function middleware(request) {
  const accessToken = request.cookies.get('access_token')
  // console.log(accessToken)
  const { pathname } = request.nextUrl

  if (publicRoutes.includes(pathname)) {
    return NextResponse.next()
  }

  if (!accessToken && !publicRoutes.includes(pathname)) {
    const loginUrl = new URL('/login', request.url)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!api|_next|_static|_vercel|[\\w-]+\\.\\w+).*)',
  ],
}