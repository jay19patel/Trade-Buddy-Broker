'use client'
// import Cookies from 'js-cookie'; 
import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ChevronLeft, ChevronRight, BookOpen, X } from "lucide-react"
import { useToast } from '@/hooks/use-toast'


export default function TradingTable() {
  const [trades, setTrades] = useState([])
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedTrade, setSelectedTrade] = useState(null)
  const [showOrderDialog, setShowOrderDialog] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()
  const tradesPerPage = 5

  const fetchTrades = async () => {
    setIsLoading(true)
    try {

      const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBY2NvdW50SWQiOiJLSDJZRCIsIkFjY291bnRFbWFpbCI6ImpheUBnbWFpbC5jb20iLCJBY2NvdW50Um9sZSI6IlVzZXIiLCJleHAiOjIwMzgxNjk5MzQsImp0aSI6IjJiZmEzOWEyLTA0MzMtNDRjYS1hNzlkLTdlM2IyY2ViZDdmNyJ9.78GtirKl3kyHqXmEk_Ntt6FILGUnVVaogbZydD26nRY";
      console.log("Cooookies is :",token)

      const response = await fetch('http://127.0.0.1:8000/order/positions?trade_today=false', {
        method: 'GET',
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch trades')
      }
      const data = await response.json()
      console.log("Positions Data is :",data.data)
      setTrades(data.data)
    } catch (error) {
      console.error('Error fetching trades:', error)
      toast({
        title: "Error",
        description: "Failed to fetch trades. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchTrades()
  }, [])

  const indexOfLastTrade = currentPage * tradesPerPage
  const indexOfFirstTrade = indexOfLastTrade - tradesPerPage
  const currentTrades = trades.slice(indexOfFirstTrade, indexOfLastTrade)

  const totalPages = Math.ceil(trades.length / tradesPerPage)

  const handleOpenOrders = (trade) => {
    setSelectedTrade(trade)
    setShowOrderDialog(true)
  }

  const handleExit = async (tradeId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/order/create_exit_order/`, {
        method: 'POST',
      })
      if (!response.ok) {
        throw new Error('Failed to exit trade')
      }
      await fetchTrades() // Refetch trades after successful exit
      toast({
        title: "Success",
        description: "Trade exited successfully.",
      })
    } catch (error) {
      console.error('Error exiting trade:', error)
      toast({
        title: "Error",
        description: "Failed to exit trade. Please try again.",
        variant: "destructive",
      })
    }
  }

  const getOrderTypeColor = (orderType) => {
    switch (orderType) {
      case 'Exit Order':
        return 'bg-red-100'
      case 'Quantity Add Order':
        return 'bg-green-100'
      case 'New Order':
        return 'bg-blue-100'
      default:
        return ''
    }
  }

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>
  }

  return (
    <div className="w-full max-w-7xl mx-auto p-2 sm:p-4 lg:p-3">
      <Card className="shadow-lg bg-white">
        <CardContent className="p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Open Positions</h2>
          <div className="overflow-x-auto -mx-6 px-6">
            <Table className="border-collapse border border-gray-200">
              <TableHeader>
                <TableRow className="bg-gray-100">
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Position ID</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Symbol</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Side</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Buy/Sell Price</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Date</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Quantity</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Margin</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {currentTrades.map((trade) => (
                  <TableRow key={trade.position_id} className="">
                    <TableCell className="py-2 px-4 border border-gray-200 font-medium">{trade.position_id}</TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">{trade.stock_symbol}</TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">
                      <span className="px-2 py-1 rounded-full bg-green-500 text-white font-semibold">
                        Buy
                      </span>
                    </TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200 font-bold">
                      ${trade.position_status === 'BUY' ? trade.buy_average : 
                        trade.position_status === 'SELL' ? trade.sell_average : 
                        trade.current_price}
                    </TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">{new Date(trade.created_date).toLocaleString()}</TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">
                      {trade.position_status === 'PENDING' ? trade.sell_quantity : trade.buy_quantity}
                    </TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">
                      ${trade.position_status === 'BUY' ? trade.buy_margin : 
                        trade.position_status === 'SELL' ? trade.sell_margin : 
                        trade.buy_margin || trade.sell_margin}
                    </TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">
                      <div className="flex space-x-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleOpenOrders(trade)}
                        >
                          <BookOpen className="h-4 w-4 mr-2" />
                          Orders
                        </Button>
                        <Button 
                          size="sm" 
                          variant="destructive"
                          onClick={() => handleExit(trade.position_id)}
                        >
                          <X className="h-4 w-4 mr-2" />
                          Exit
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
              Showing {indexOfFirstTrade + 1} to {Math.min(indexOfLastTrade, trades.length)} of {trades.length} entries
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

      <Dialog open={showOrderDialog} onOpenChange={setShowOrderDialog}>
        <DialogContent className="sm:max-w-[600px] w-[95vw] max-h-[80vh] overflow-y-auto p-4 sm:p-6 bg-white">
          <DialogHeader className="mb-4">
            <DialogTitle className="text-xl font-semibold">Orders for {selectedTrade?.stock_symbol}</DialogTitle>
          </DialogHeader>
          <div className="overflow-x-auto -mx-4 sm:mx-0">
            <Table className="border-collapse border border-gray-200">
              <TableHeader>
                <TableRow className="bg-gray-100">
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Order ID</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Order Type</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Side</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Quantity</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Price</TableHead>
                  <TableHead className="py-3 px-4 border border-gray-200 font-semibold">Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {selectedTrade?.orders.map((order) => (
                  <TableRow key={order.order_id} className={`${getOrderTypeColor(order.order_types)}`}>
                    <TableCell className="py-2 px-4 border border-gray-200">{order.order_id}</TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">{order.order_types}</TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">{order.order_side}</TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">{order.quantity}</TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">${order.limit_price || 'N/A'}</TableCell>
                    <TableCell className="py-2 px-4 border border-gray-200">{new Date(order.order_datetime).toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}