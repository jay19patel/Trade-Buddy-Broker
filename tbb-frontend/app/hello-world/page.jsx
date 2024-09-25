import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Mail, User, Send, Code, Package, ShoppingCart, BarChart, CreditCard } from "lucide-react"

export default function ContactPage() {
  return (
    <div className="container mx-auto px-4 py-8 bg-gradient-to-br from-purple-100 to-blue-100 min-h-screen">
      <h1 className="text-4xl font-bold text-center mb-8 text-purple-800">Contact Us</h1>
      
      <div className="grid md:grid-cols-2 gap-8">
        <Card className="bg-white shadow-lg">
          <CardHeader className="bg-purple-600 text-white">
            <CardTitle className="flex items-center"><User className="mr-2" /> Basic Details</CardTitle>
            <CardDescription className="text-purple-100">You can reach us using the following information:</CardDescription>
          </CardHeader>
          <CardContent className="mt-4">
            <p className="flex items-center mb-2"><Mail className="mr-2 text-purple-600" /> <strong>Email:</strong> contact@example.com</p>
            <p className="flex items-center"><User className="mr-2 text-purple-600" /> <strong>Name:</strong> Example Company</p>
          </CardContent>
        </Card>
        
        <Card className="bg-white shadow-lg">
          <CardHeader className="bg-blue-600 text-white">
            <CardTitle className="flex items-center"><Send className="mr-2" /> Send us a message</CardTitle>
            <CardDescription className="text-blue-100">Fill out this form and we'll get back to you as soon as possible.</CardDescription>
          </CardHeader>
          <CardContent className="mt-4">
            <form className="space-y-4">
              <Input placeholder="Your Email" type="email" required className="border-blue-300 focus:border-blue-500" />
              <Input placeholder="Subject" required className="border-blue-300 focus:border-blue-500" />
              <Textarea placeholder="Your Message" required className="border-blue-300 focus:border-blue-500" />
              <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700">Send Message</Button>
            </form>
          </CardContent>
        </Card>
      </div>
      
      <Card className="mt-8 bg-white shadow-lg">
        <CardHeader className="bg-green-600 text-white">
          <CardTitle className="flex items-center"><Code className="mr-2" /> Our APIs</CardTitle>
          <CardDescription className="text-green-100">Explore our powerful APIs to integrate with our services.</CardDescription>
        <a href={"http://localhost:8080/docs"} className="text-white hover:underline mt-2 inline-block">Learn more</a>
        </CardHeader>
        <CardContent className="mt-4">
          <ul className="space-y-4">
            {[
              { icon: User, title: "User Management API", description: "Manage user accounts and authentication.", link: "/api/users" },
              { icon: Package, title: "Product Catalog API", description: "Access our extensive product database.", link: "/api/products" },
              { icon: ShoppingCart, title: "Order Processing API", description: "Integrate order management into your systems.", link: "/api/orders" },
              { icon: BarChart, title: "Analytics API", description: "Retrieve detailed analytics and reports.", link: "/api/analytics" },
              { icon: CreditCard, title: "Payment Gateway API", description: "Securely process payments through our platform.", link: "/api/payments" },
            ].map((api, index) => (
              <li key={index} className="bg-gray-100 p-4 rounded-lg">
                <div className="flex items-center mb-2">
                  <api.icon className="mr-2 text-green-600" />
                  <strong className="text-lg text-green-800">{api.title}</strong>
                </div>
                <p className="text-gray-600 mb-2">{api.description}</p>
                <div className="bg-gray-200 p-2 rounded text-sm font-mono">
                  GET {api.link}
                </div>
                {/* <a href={api.link} className="text-blue-500 hover:underline mt-2 inline-block">Learn more</a> */}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}