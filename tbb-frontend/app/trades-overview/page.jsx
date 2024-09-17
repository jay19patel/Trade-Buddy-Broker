"use client"

import React, { useState } from "react"
import { ArrowDown, ArrowUp, DollarSign } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const indices = [
  { date: "2023-06-01", name: "NIFTY50", ceProfit: 0, ceProfitAmount: 0, peProfit: 1, peProfitAmount: 3895, ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0, netTrades: 1, netAmount: 3895 },
  { date: "2023-06-15", name: "BANKNIFTY", ceProfit: 0, ceProfitAmount: 0, peProfit: 1, peProfitAmount: 14697, ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0, netTrades: 1, netAmount: 1200 },
  { date: "2023-07-01", name: "SENSEX", ceProfit: 0, ceProfitAmount: 0, peProfit: 0, peProfitAmount: 0, ceLoss: 1, ceLossAmount: 3186, peLoss: 0, peLossAmount: 0, netTrades: 1, netAmount: -3186 },
  { date: "2023-08-15", name: "BANKEX", ceProfit: 0, ceProfitAmount: 0, peProfit: 0, peProfitAmount: 300, ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0, netTrades: 0, netAmount: 500 },
  { date: "2023-09-15", name: "BANKEX", ceProfit: 0, ceProfitAmount: 0, peProfit: 0, peProfitAmount: 300, ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0, netTrades: 0, netAmount: 800 },
  { date: "2023-10-15", name: "BANKEX", ceProfit: 0, ceProfitAmount: 0, peProfit: 0, peProfitAmount: 300, ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0, netTrades: 0, netAmount: 900 },
  { date: "2023-11-15", name: "BANKEX", ceProfit: 0, ceProfitAmount: 0, peProfit: 0, peProfitAmount: 300, ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0, netTrades: 0, netAmount: 1200 },
  { date: "2023-12-15", name: "BANKEX", ceProfit: 0, ceProfitAmount: 0, peProfit: 0, peProfitAmount: 300, ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0, netTrades: 0, netAmount: 1500 },
  { date: "2024-01-15", name: "BANKEX", ceProfit: 0, ceProfitAmount: 0, peProfit: 0, peProfitAmount: 300, ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0, netTrades: 0, netAmount: 1900 },
  { date: "2024-02-15", name: "BANKEX", ceProfit: 0, ceProfitAmount: 0, peProfit: 0, peProfitAmount: 300, ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0, netTrades: 0, netAmount: 2200 },
]

export default function TradingAnalysisDashboard() {
  const [dateFilter, setDateFilter] = useState("all")

  const filterIndices = () => {
    const today = new Date()
    const oneMonthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())

    return indices.filter(index => {
      const indexDate = new Date(index.date)
      if (dateFilter === "today") {
        return indexDate.toDateString() === today.toDateString()
      } else if (dateFilter === "1month") {
        return indexDate >= oneMonthAgo && indexDate <= today
      }
      return true // "all" filter
    })
  }

  const filteredIndices = filterIndices()

  const totals = filteredIndices.reduce((acc, index) => ({
    ceProfit: acc.ceProfit + index.ceProfit,
    ceProfitAmount: acc.ceProfitAmount + index.ceProfitAmount,
    peProfit: acc.peProfit + index.peProfit,
    peProfitAmount: acc.peProfitAmount + index.peProfitAmount,
    ceLoss: acc.ceLoss + index.ceLoss,
    ceLossAmount: acc.ceLossAmount + index.ceLossAmount,
    peLoss: acc.peLoss + index.peLoss,
    peLossAmount: acc.peLossAmount + index.peLossAmount,
    netTrades: acc.netTrades + index.netTrades,
    netAmount: acc.netAmount + index.netAmount,
  }), {
    ceProfit: 0, ceProfitAmount: 0, peProfit: 0, peProfitAmount: 0,
    ceLoss: 0, ceLossAmount: 0, peLoss: 0, peLossAmount: 0,
    netTrades: 0, netAmount: 0
  })

  const getTextStyle = (value) => {
    if (value === 0) return "text-gray-500"
    return value > 0 ? "text-green-700 font-bold" : "text-red-700 font-bold"
  }

  return (
    <div className="container mx-auto p-4 space-y-8">
      <h1 className="text-3xl font-bold mb-4">Trading Analysis Dashboard</h1>
      
      <Card className="w-full bg-white">
        <CardHeader>
          <CardTitle>Performance Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart
              data={indices}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="netAmount" name="Net Amount" stroke="#8884d8" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Analysis Table</h2>
        <div className="mb-4 flex gap-2">
          <Button
            onClick={() => setDateFilter("today")}
            variant={dateFilter === "today" ? "default" : "outline"}
          >
            Today
          </Button>
          <Button
            onClick={() => setDateFilter("1month")}
            variant={dateFilter === "1month" ? "default" : "outline"}
          >
            1 Month
          </Button>
          <Button
            onClick={() => setDateFilter("all")}
            variant={dateFilter === "all" ? "default" : "outline"}
          >
            All
          </Button>
        </div>
        <div className="border border-gray-300 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="w-[100px] border-r border-b border-gray-300 p-2 text-left">Index</th>
                <th className="bg-green-100 border-r border-b border-gray-300 p-2 text-left">CE Profit</th>
                <th className="bg-green-100 border-r border-b border-gray-300 p-2 text-left">CE Profit Amount</th>
                <th className="bg-green-100 border-r border-b border-gray-300 p-2 text-left">PE Profit</th>
                <th className="bg-green-100 border-r border-b border-gray-300 p-2 text-left">PE Profit Amount</th>
                <th className="bg-red-100 border-r border-b border-gray-300 p-2 text-left">CE Loss</th>
                <th className="bg-red-100 border-r border-b border-gray-300 p-2 text-left">CE Loss Amount</th>
                <th className="bg-red-100 border-r border-b border-gray-300 p-2 text-left">PE Loss</th>
                <th className="bg-red-100 border-r border-b border-gray-300 p-2 text-left">PE Loss Amount</th>
                <th className="bg-gray-100 border-r border-b border-gray-300 p-2 text-left">Net Trades</th>
                <th className="bg-gray-100 border-b border-gray-300 p-2 text-left">Net Amount</th>
              </tr>
            </thead>
            <tbody>
              {filteredIndices.map((index) => (
                <tr key={index.name} className="border-b border-gray-300 last:border-b-0">
                  <td className="font-medium border-r border-gray-300 p-2">{index.name}</td>
                  <td className={`bg-green-100 border-r border-gray-300 p-2 ${getTextStyle(index.ceProfit)}`}>{index.ceProfit}</td>
                  <td className={`bg-green-100 border-r border-gray-300 p-2 ${getTextStyle(index.ceProfitAmount)}`}>{index.ceProfitAmount}</td>
                  <td className={`bg-green-100 border-r border-gray-300 p-2 ${getTextStyle(index.peProfit)}`}>{index.peProfit}</td>
                  <td className={`bg-green-100 border-r border-gray-300 p-2 ${getTextStyle(index.peProfitAmount)}`}>{index.peProfitAmount}</td>
                  <td className={`bg-red-100 border-r border-gray-300 p-2 ${getTextStyle(-index.ceLoss)}`}>{index.ceLoss}</td>
                  <td className={`bg-red-100 border-r border-gray-300 p-2 ${getTextStyle(-index.ceLossAmount)}`}>{index.ceLossAmount}</td>
                  <td className={`bg-red-100 border-r border-gray-300 p-2 ${getTextStyle(-index.peLoss)}`}>{index.peLoss}</td>
                  <td className={`bg-red-100 border-r border-gray-300 p-2 ${getTextStyle(-index.peLossAmount)}`}>{index.peLossAmount}</td>
                  <td className={`bg-gray-100 border-r border-gray-300 p-2 ${getTextStyle(index.netTrades)}`}>{index.netTrades}</td>
                  <td className={`bg-gray-100 p-2 ${getTextStyle(index.netAmount)}`}>{index.netAmount}</td>
                </tr>
              ))}
              <tr className="font-bold bg-gray-200">
                <td className="border-r border-gray-300 p-2">Overall</td>
                <td className={`border-r border-gray-300 p-2 ${getTextStyle(totals.ceProfit)}`}>{totals.ceProfit}</td>
                <td className={`border-r border-gray-300 p-2 ${getTextStyle(totals.ceProfitAmount)}`}>{totals.ceProfitAmount}</td>
                <td className={`border-r border-gray-300 p-2 ${getTextStyle(totals.peProfit)}`}>{totals.peProfit}</td>
                <td className={`border-r border-gray-300 p-2 ${getTextStyle(totals.peProfitAmount)}`}>{totals.peProfitAmount}</td>
                <td className={`border-r border-gray-300 p-2 ${getTextStyle(-totals.ceLoss)}`}>{totals.ceLoss}</td>
                <td className={`border-r border-gray-300 p-2 ${getTextStyle(-totals.ceLossAmount)}`}>{totals.ceLossAmount}</td>
                <td className={`border-r border-gray-300 p-2 ${getTextStyle(-totals.peLoss)}`}>{totals.peLoss}</td>
                <td className={`border-r border-gray-300 p-2 ${getTextStyle(-totals.peLossAmount)}`}>{totals.peLossAmount}</td>
                <td className={`border-r border-gray-300 p-2 ${getTextStyle(totals.netTrades)}`}>{totals.netTrades}</td>
                <td className={`p-2 ${getTextStyle(totals.netAmount)}`}>{totals.netAmount}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-green-100">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Total Profit</h2>
              <p className="text-2xl font-bold text-green-700">{totals.ceProfitAmount + totals.peProfitAmount}</p>
            </div>
            <ArrowUp className="h-8 w-8 text-green-700" />
          </CardContent>
        </Card>
        <Card className="bg-red-100">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Total Loss</h2>
              <p className="text-2xl font-bold text-red-700">{totals.ceLossAmount + totals.peLossAmount}</p>
            </div>
            <ArrowDown className="h-8 w-8 text-red-700" />
          </CardContent>
        </Card>
        <Card className="bg-blue-100">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Net Amount</h2>
              <p className="text-2xl font-bold text-blue-700">{totals.netAmount}</p>
            </div>
            <DollarSign className="h-8 w-8 text-blue-700" />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}