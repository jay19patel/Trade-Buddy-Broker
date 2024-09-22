'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Search, TrendingUp, TrendingDown, DollarSign, BarChart2, Activity, X, ShoppingCart, Banknote } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Card, CardContent } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"

export default function StockSearchApp() {
  const [searchTerm, setSearchTerm] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedStock, setSelectedStock] = useState(null)
  const [showBuyDialog, setShowBuyDialog] = useState(false)
  const [showSellDialog, setShowSellDialog] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const [isStockSelected, setIsStockSelected] = useState(false)
  const dropdownRef = useRef(null)
  const inputRef = useRef(null)
  const { toast } = useToast()

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target) && !inputRef.current.contains(event.target)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (searchTerm.length >= 3 && !isStockSelected) {
        fetchSearchResults()
      } else {
        setSearchResults([])
        setShowDropdown(false)
      }
    }, 300)

    return () => clearTimeout(delayDebounceFn)
  }, [searchTerm, isStockSelected])

  const fetchSearchResults = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/home/search?q=${searchTerm}`)
      const data = await response.json() 
      setSearchResults(data)
      setShowDropdown(true)
    } catch (error) {
    } finally {
      setIsLoading(false)
    }
  }

  const handleStockSelect = async (stock) => {
    setSearchTerm(stock.title)
    setShowDropdown(false)
    setIsStockSelected(true)

    try {
      const symbolId = stock.nse_scrip_code || stock.bse_scrip_code || stock.id;
      const response = await fetch(`http://localhost:8000/home/find?type_of_symbol=${stock.entity_type}&symbol_id=${symbolId}`)
      const detailData = await response.json()
      setSelectedStock(detailData)
    } catch (error) {
    }
  }

  const handleSearchInputChange = (e) => {
    setSearchTerm(e.target.value)
    setIsStockSelected(false)
  }

  const addOrder = async (orderDetails) => {
    console.log("Order Created Data is :",orderDetails)

    // try {
    //   const symbolId = stock.nse_scrip_code || stock.bse_scrip_code || stock.id;
    //   const response = await fetch(`http://localhost:8000/home/find?type_of_symbol=${stock.entity_type}&symbol_id=${symbolId}`,
    //   )
    //   const detailData = await response.json()
    //   setSelectedStock(detailData)
    // } catch (error) {
    // }



    setShowBuyDialog(false)
    setShowSellDialog(false)
    toast({
      title: "Order Submitted",
      description: `${orderDetails.type.toUpperCase()} order for ${orderDetails.stock.name} has been placed.`,
      duration: 3000,
    })
  }

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      <div className="relative mb-4">
        <div className="relative bg-white">
          <Input
            ref={inputRef}
            type="text"
            placeholder="Search for a stock..."
            value={searchTerm}
            onChange={handleSearchInputChange}
            className="pl-10 pr-4 py-2 w-full"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        </div>
        {isLoading && <div className="mt-2 text-center">Loading...</div>}
        {showDropdown && searchResults.length > 0 && (
          <div 
            ref={dropdownRef}
            className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg overflow-hidden"
            style={{
              maxHeight: '60vh',
              overflowY: 'auto'
            }}
          >
            {searchResults.map((result) => (
              <div
                key={result.search_id}
                className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                onClick={() => handleStockSelect(result)}
              >
                <div className="font-medium">{result.title}</div>
                <div className="text-sm text-gray-500">{result.entity_type}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      <section className="mb-8">
        {selectedStock ? (
          <Card className="bg-white relative">
            <CardContent className="p-6">
              <Button
                variant="ghost"
                size="icon"
                className="absolute top-2 right-2"
                onClick={() => {
                  setSelectedStock(null)
                  setSearchTerm('')
                  setIsStockSelected(false)
                }}
              >
                <X className="h-4 w-4" />
              </Button>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="col-span-1 md:col-span-2 lg:col-span-3">
                  <h2 className="text-3xl font-bold mb-2">{selectedStock.name}</h2>
                  <div className="flex items-center space-x-4">
                    <span className="text-2xl font-semibold"> ₹{selectedStock.ltp.toFixed(2)}</span>
                    <span className={`text-lg font-medium ${selectedStock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {selectedStock.change >= 0 ? <TrendingUp className="inline mr-1" /> : <TrendingDown className="inline mr-1" />}
                      {selectedStock.change.toFixed(2)} ({selectedStock.changePercent.toFixed(2)}%)
                    </span>
                  </div>
                </div>
                <StockDataCard title="Market Data" icon={<BarChart2 className="h-5 w-5" />}>
                  <DataItem label="Open" value={selectedStock.open.toFixed(2)} />
                  <DataItem label="High" value={selectedStock.high.toFixed(2)} />
                  <DataItem label="Low" value={selectedStock.low.toFixed(2)} />
                  <DataItem label="Volume" value={selectedStock.volume.toLocaleString()} />
                </StockDataCard>
                {/* Uncomment and adjust these cards if you have the data available */}
                {/* <StockDataCard title="Financial Metrics" icon={<DollarSign className="h-5 w-5" />}>
                  <DataItem label="Market Cap" value={`$${(selectedStock.marketCap / 1e9).toFixed(2)}B`} />
                  <DataItem label="P/E Ratio" value={selectedStock.pe.toFixed(2)} />
                  <DataItem label="Dividend" value={selectedStock.dividend.toFixed(2)} />
                  <DataItem label="Yield" value={`${selectedStock.yield.toFixed(2)}%`} />
                </StockDataCard>
                <StockDataCard title="Technical Indicators" icon={<Activity className="h-5 w-5" />}>
                  <DataItem label="EMA" value={selectedStock.ema.toFixed(2)} />
                  <DataItem label="RSI" value={selectedStock.rsi.toFixed(2)} />
                </StockDataCard> */}
              </div>
              <div className="flex space-x-4 mt-6">
                <Dialog open={showBuyDialog} onOpenChange={setShowBuyDialog}>
                  <DialogTrigger asChild>
                    <Button className="bg-blue-500 hover:bg-blue-600 text-white">
                      <ShoppingCart className="mr-2 h-4 w-4" />
                      Buy
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-blue-50 max-w-4xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle className="text-2xl font-bold text-blue-800">
                        Buy {selectedStock.name}
                      </DialogTitle>
                    </DialogHeader>
                    <TradeForm stock={selectedStock} type="buy" onSubmit={addOrder} />
                  </DialogContent>
                </Dialog>
                <Dialog open={showSellDialog} onOpenChange={setShowSellDialog}>
                  <DialogTrigger asChild>
                    <Button className="bg-red-500 hover:bg-red-600 text-white">
                      <Banknote className="mr-2 h-4 w-4" />
                      Sell
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-red-50 max-w-4xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle className="text-2xl font-bold text-red-800">
                        Sell {selectedStock.name}
                      </DialogTitle>
                    </DialogHeader>
                    <TradeForm stock={selectedStock} type="sell" onSubmit={addOrder} />
                  </DialogContent>
                </Dialog>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="bg-white">
            <CardContent className="p-6">
              <p className="text-center text-gray-500">Search and select a stock to view details</p>
            </CardContent>
          </Card>
        )}
      </section>
    </div>
  )
}

function StockDataCard({ title, icon, children }) {
  return (
    <div className="bg-gray-50 p-4 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-3 flex items-center">
        {icon}
        <span className="ml-2">{title}</span>
      </h3>
      <div className="grid grid-cols-2 gap-2">
        {children}
      </div>
    </div>
  )
}

function DataItem({ label, value }) {
  const isNegative = typeof value === 'string' && value.startsWith('-')
  return (
    <div>
      <span className="text-sm text-gray-500">{label}:</span>
      <span className={`ml-1 font-medium ${isNegative ? 'text-red-600' : 'text-green-600'}`}>{value}</span>
    </div>
  )
}

function TradeForm({ stock, type, onSubmit }) {
  const [quantity, setQuantity] = useState('')
  const [limitPrice, setLimitPrice] = useState('')
  const [triggerPrice, setTriggerPrice] = useState('')
  const [stoplossTriggerPrice, setStoplossTriggerPrice] = useState('')
  const [targetTriggerPrice, setTargetTriggerPrice] = useState('')
  const [stoplossLimitPrice, setStoplossLimitPrice] = useState('')
  const [targetLimitPrice, setTargetLimitPrice] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      stock,
      type,
      quantity,
      limitPrice,
      triggerPrice,
      stoplossTriggerPrice,
      targetTriggerPrice,
      stoplossLimitPrice,
      targetLimitPrice
    })
  }

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Price</label>
        <Input type="text" value={stock.ltp.toFixed(2)} readOnly className="bg-gray-100" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Quantity</label>
        <Input type="number" value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Limit Price</label>
        <Input type="number" value={limitPrice} onChange={(e) => setLimitPrice(e.target.value)} step="0.01" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Trigger Price</label>
        <Input type="number" value={triggerPrice} onChange={(e) => setTriggerPrice(e.target.value)} step="0.01" />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Stoploss Limit Price</label>
        <Input type="number" value={stoplossLimitPrice} onChange={(e) => setStoplossLimitPrice(e.target.value)} step="0.01" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Stoploss Trigger Price</label>
        <Input type="number" value={stoplossTriggerPrice} onChange={(e) => setStoplossTriggerPrice(e.target.value)} step="0.01" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Target Limit Price</label>
        <Input type="number" value={targetLimitPrice} onChange={(e) => setTargetLimitPrice(e.target.value)} step="0.01" />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Target Trigger Price</label>
        <Input type="number" value={targetTriggerPrice} onChange={(e) => setTargetTriggerPrice(e.target.value)} step="0.01" />
      </div>
      
      
      <div className="sm:col-span-2">
        <Button type="submit" className={`w-full ${type === 'buy' ? 'bg-blue-500 hover:bg-blue-600' : 'bg-red-500 hover:bg-red-600'} text-white`}>
          {type === 'buy' ? <ShoppingCart className="mr-2 h-4 w-4" /> : <Banknote className="mr-2 h-4 w-4" />}
          {type === 'buy' ? 'Buy' : 'Sell'} Stock
        </Button>
      </div>
    </form>
  )
}