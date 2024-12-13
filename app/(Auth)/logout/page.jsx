'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Cookies from 'js-cookie'

export default function LogoutPage() {
  const router = useRouter()

  useEffect(() => {
    // Remove cookies
    const allCookies = Cookies.get(); // Get all cookies
    for (const cookie in allCookies) {
      Cookies.remove(cookie); // Remove each cookie
  }
    router.push("/login")
  }, [router])

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Logging out...</h1>
        <p className="text-gray-600">Please wait while we log you out.</p>
      </div>
    </div>
  )
}