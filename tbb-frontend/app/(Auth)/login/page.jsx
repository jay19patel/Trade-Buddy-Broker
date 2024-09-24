"use client"
import Cookies from 'js-cookie'; 
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import axios from 'axios';
import { useToast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const { toast } = useToast()
  const  router = useRouter()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setIsLoading(true)

    try {
      const response = await axios.post('http://127.0.0.1:8080/auth/login_account', {
        user_id: email,
        password: password
      },
      {
        withCredentials: true
      }
    
    );
    Cookies.set("access_token",response.data.payload.access_token)
    Cookies.set("full_name",response.data.payload.full_name)
      router.push("/")
      toast({
        title: "Authentication Success",
        description: `Sucessfully Login`,
        duration: 3000,
      })      
    } catch (error) {
      toast({
        title: "Authentication Failed",
        description: error.response,
        duration: 3000,
      })
    }
    finally{
    }



    setIsLoading(false)
  }

  return (
    <div className="flex items-center justify-center p-4">
      <Card className="w-full bg-white max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">Login to Trade Buddy</CardTitle>
          <CardDescription className="text-center">Enter your credentials to access your account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email_id">Email</Label>
              <Input
                id="email_id"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)} // Update email state
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)} // Update password state
                required
              />
            </div>
            <Button type="submit" className="w-full bg-blue-900 text-white hover:text-black" disabled={isLoading}>
              {isLoading ? "Logging in..." : "Login"}
            </Button>
          </form>
          <p className="text-center mt-4 text-sm">
            Don't have an account?{" "}
            <Link href="/registration" className="text-primary hover:underline">
              Register here
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
