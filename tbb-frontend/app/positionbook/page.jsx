
"use client"
import React, { useState, useEffect } from 'react'
import { Search, Filter, X, ExternalLink, BookOpen, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Card, CardContent } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

// Dummy data for the order book (expanded to 50 items for pagination demo)
const dummyOrders = Array(20).fill().map((_, index) => ({
  id: index + 1,
  orderId: `ORD${String(index + 1).padStart(3, '0')}`,
  symbol: ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB'][Math.floor(Math.random() * 5)],
  type: Math.random() > 0.5 ? 'BUY' : 'SELL',
  quantity: Math.floor(Math.random() * 100) + 1,
  price: (Math.random() * 1000 + 100).toFixed(2),
  slPrice: (Math.random() * 1000 + 100).toFixed(2),
  targetPrice: (Math.random() * 1000 + 100).toFixed(2),
  status: ['Open', 'Executed', 'Pending', 'Exited'][Math.floor(Math.random() * 4)],
  validity: ['Intraday', 'Swing', 'Long'][Math.floor(Math.random() * 3)],
  datetime: new Date(Date.now() - Math.floor(Math.random() * 10000000000)).toLocaleString(),
}))

export default function EnhancedOrderBook() {
  const [orders, setOrders] = useState(dummyOrders)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [validityFilter, setValidityFilter] = useState('All')
  const [showExitDialog, setShowExitDialog] = useState(false)
  const [showOrderBookDialog, setShowOrderBookDialog] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(6)

  const filteredOrders = orders.filter(order => 
    (order.orderId.toLowerCase().includes(searchTerm.toLowerCase()) || 
     order.symbol.toLowerCase().includes(searchTerm.toLowerCase())) &&
    (statusFilter === 'All' || order.status === statusFilter) &&
    (validityFilter === 'All' || order.validity === validityFilter)
  )

  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = filteredOrders.slice(indexOfFirstItem, indexOfLastItem)

  const totalPages = Math.ceil(filteredOrders.length / itemsPerPage)

  const handleExit = (orderId) => {
    setOrders(orders.map(order => 
      order.orderId === orderId ? { ...order, status: 'Exited' } : order
    ))
    setShowExitDialog(false)
  }

  const clearFilters = () => {
    setSearchTerm('')
    setStatusFilter('All')
    setValidityFilter('All')
  }

  return (
    <div className="w-full max-w-7xl mx-auto p-2 sm:p-4 lg:p-3">
      <Card className="shadow-lg bg-white">
        <CardContent className="p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Order Book</h2>
          <div className="flex flex-col space-y-4 mb-6">
            <div className="flex flex-wrap items-center gap-4">
              <div className="relative flex-grow">
                <Input
                  type="text"
                  placeholder="Search by Order ID or Symbol"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 w-full"
                />
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by Status" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="All">All Statuses</SelectItem>
                  <SelectItem value="Open">Open</SelectItem>
                  <SelectItem value="Executed">Executed</SelectItem>
                  <SelectItem value="Pending">Pending</SelectItem>
                  <SelectItem value="Exited">Exited</SelectItem>
                </SelectContent>
              </Select>
              <Select value={validityFilter} onValueChange={setValidityFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by Validity" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="All">All Validities</SelectItem>
                  <SelectItem value="Intraday">Intraday</SelectItem>
                  <SelectItem value="Swing">Swing</SelectItem>
                  <SelectItem value="Long">Long</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={clearFilters} variant="outline" className="whitespace-nowrap">
                Clear Filters
              </Button>
            </div>
          </div>
          <div className="overflow-x-auto -mx-6 px-6">
            <Table>
              <TableHeader>
                <TableRow className="bg-gray-100">
                  <TableHead className="py-3 px-4">Order ID</TableHead>
                  <TableHead className="py-3 px-4">Symbol</TableHead>
                  <TableHead className="py-3 px-4">Type</TableHead>
                  <TableHead className="py-3 px-4">Qty</TableHead>
                  <TableHead className="py-3 px-4">Price</TableHead>
                  <TableHead className="py-3 px-4">SL</TableHead>
                  <TableHead className="py-3 px-4">Target</TableHead>
                  <TableHead className="py-3 px-4">Status</TableHead>
                  <TableHead className="py-3 px-4">Validity</TableHead>
                  <TableHead className="py-3 px-4">DateTime</TableHead>
                  <TableHead className="py-3 px-4">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {currentItems.map((order) => (
                  <TableRow key={order.id} className="hover:bg-gray-50">
                    <TableCell className="py-2 px-4 font-medium">{order.orderId}</TableCell>
                    <TableCell className="py-2 px-4">{order.symbol}</TableCell>
                    <TableCell className={`py-2 px-4 ${order.type === 'BUY' ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}`}>
                      {order.type}
                    </TableCell>
                    <TableCell className="py-2 px-4">{order.quantity}</TableCell>
                    <TableCell className="py-2 px-4 font-bold">${order.price}</TableCell>
                    <TableCell className="py-2 px-4 text-red-600 font-bold">${order.slPrice}</TableCell>
                    <TableCell className="py-2 px-4 text-green-600 font-bold">${order.targetPrice}</TableCell>
                    <TableCell className="py-2 px-4">{order.status}</TableCell>
                    <TableCell className="py-2 px-4">{order.validity}</TableCell>
                    <TableCell className="py-2 px-4">{order.datetime}</TableCell>
                    <TableCell className="py-2 px-4">
                      <div className="flex space-x-2">
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => {
                            setSelectedOrder(order)
                            setShowExitDialog(true)
                          }}
                        >
                          Exit
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setSelectedOrder(order)
                            setShowOrderBookDialog(true)
                          }}
                        >
                          <BookOpen className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <div className="mt-6 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {indexOfFirstItem + 1} to {Math.min(indexOfLastItem, filteredOrders.length)} of {filteredOrders.length} entries
            </div>
            <div className="flex items-center space-x-2">
              <Button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                variant="outline"
                size="sm"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <Button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  variant={currentPage === page ? "default" : "outline"}
                  size="sm"
                >
                  {page}
                </Button>
              ))}
              <Button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                variant="outline"
                size="sm"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Dialog open={showExitDialog} onOpenChange={setShowExitDialog}>
        <DialogContent className="sm:max-w-[425px] p-6 bg-white">
          <DialogHeader className="mb-4">
            <DialogTitle className="text-xl font-semibold">Confirm Exit</DialogTitle>
          </DialogHeader>
          <p className="mb-6">Are you sure you want to exit this order?</p>
          <div className="flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-2">
            <Button className="w-full sm:w-auto bg-red-600" variant="destructive" onClick={() => setShowExitDialog(false)}>Cancel</Button>
            <Button className="w-full sm:w-auto bg-blue-600" onClick={() => handleExit(selectedOrder?.orderId)}>Confirm</Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showOrderBookDialog} onOpenChange={setShowOrderBookDialog}>
        <DialogContent className="sm:max-w-[800px] w-[95vw] max-h-[80vh] overflow-y-auto p-4 sm:p-6 bg-white">
          <DialogHeader className="mb-4">
            <DialogTitle className="text-xl font-semibold">Order Book for {selectedOrder?.symbol}</DialogTitle>
          </DialogHeader>
          <div className="overflow-x-auto -mx-4 sm:mx-0">
            <Table>
              <TableHeader>
                <TableRow className="bg-gray-100">
                  <TableHead className="py-3 px-4">Order ID</TableHead>
                  <TableHead className="py-3 px-4">Action Type</TableHead>
                  <TableHead className="py-3 px-4">Status</TableHead>
                  <TableHead className="py-3 px-4">DateTime</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow className="hover:bg-gray-50">
                  <TableCell className="py-2 px-4">{selectedOrder?.orderId}</TableCell>
                  <TableCell className="py-2 px-4">Place Order</TableCell>
                  <TableCell className="py-2 px-4">Executed</TableCell>
                  <TableCell className="py-2 px-4">{selectedOrder?.datetime}</TableCell>
                </TableRow>
                <TableRow className="hover:bg-gray-50">
                  <TableCell className="py-2 px-4">{selectedOrder?.orderId}</TableCell>
                  <TableCell className="py-2 px-4">Modify SL</TableCell>
                  <TableCell className="py-2 px-4">Executed</TableCell>
                  <TableCell className="py-2 px-4">{new Date(new Date(selectedOrder?.datetime).getTime() + 3600000).toLocaleString()}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}