"use client"
import React from 'react'
import Cookies from 'js-cookie'
import { useRouter } from 'next/navigation'
const page = () => {
    const router = useRouter()
    Cookies.remove("access_token")
    Cookies.remove("full_name")
    router.push("/login")
  return (
    <div>Logout.....</div>
  )
}

export default page