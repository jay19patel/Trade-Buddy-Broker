
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import Link from "next/link"

export default function RegisterPage() {
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setIsLoading(true)
    // Here you would typically send the form data to your API
    console.log("Form submitted")
    setIsLoading(false)
  }

  return (
    <div className="flex items-center justify-center  p-4">
      <Card className="w-full bg-white max-w-4xl">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">Register for Trade Buddy</CardTitle>
          <CardDescription className="text-center">Create your account to start trading</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="email_id">Email</Label>
                <Input id="email_id" type="email" placeholder="Enter your email" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" placeholder="Enter your password" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max_trad_per_day">Max Trades Per Day</Label>
                <Input id="max_trad_per_day" type="number" placeholder="Enter max trades" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="base_stoploss">Base Stoploss (%)</Label>
                <Input id="base_stoploss" type="number" placeholder="Enter base stoploss" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="base_target">Base Target (%)</Label>
                <Input id="base_target" type="number" placeholder="Enter base target" required />
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="trailing_status" />
                <Label htmlFor="trailing_status">Trailing Status</Label>
              </div>
              <div className="space-y-2">
                <Label htmlFor="trailing_stoploss">Trailing Stoploss (%)</Label>
                <Input id="trailing_stoploss" type="number" placeholder="Enter trailing stoploss" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="trailing_target">Trailing Target (%)</Label>
                <Input id="trailing_target" type="number" placeholder="Enter trailing target" required />
              </div>
              
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input id="description" placeholder="Enter description" />
            </div>
            <Button type="submit" className="w-full bg-blue-900 text-white hover:text-black" disabled={isLoading}>
              {isLoading ? "Registering..." : "Register"}
            </Button>
          </form>
          <p className="text-center mt-4 text-sm">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline">
              Login here
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}