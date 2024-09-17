import Link from 'next/link'
import { ArrowDownIcon, ArrowUpIcon, PlusIcon } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"

export default function Dashboard() {
  // Sample data - replace with your actual data
  const scoreBoard = {
    sumTrades: 100,
    openTrades: 5,
    closedTrades: 95,
    positiveTrades: 70,
    negativeTrades: 30,
    winRate: 70,
    growth: 15,
    balance: 10000
  }

  const openTrades = [
    { id: 1, symbol: "AAPL", buyPrice: 150, sl: 145, target: 160, buyDateTime: "2023-06-01 10:00", status: "Open" },
    { id: 2, symbol: "GOOGL", buyPrice: 2500, sl: 2450, target: 2550, buyDateTime: "2023-06-02 11:00", status: "Open" },
  ]

  const closedTrades = [
    { id: 3, symbol: "MSFT", buyPrice: 300, sellPrice: 310, buyDateTime: "2023-05-28 09:00", sellDateTime: "2023-05-30 14:00", quantity: 10, pnl: 100 },
    { id: 4, symbol: "AMZN", buyPrice: 3200, sellPrice: 3150, buyDateTime: "2023-05-29 10:00", sellDateTime: "2023-05-31 15:00", quantity: 5, pnl: -250 },
  ]

  return (
    <div className="min-h-screen  p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-blue-900">Trading Dashboard</h1>
          <Link href="/create-order">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white font-bold">
              <PlusIcon className="mr-2 h-4 w-4" /> New Trade
            </Button>
          </Link>
        </div>
        
        {/* Score Board */}
        <div className="grid grid-cols-3 gap-4 md:grid-cols-3 lg:grid-cols-6 mb-8">
          <ScoreCard title="Sum Trades" value={scoreBoard.sumTrades} />
          <ScoreCard title="Open/Close" value={`${scoreBoard.openTrades}/${scoreBoard.closedTrades}`} />
          <ScoreCard title="Pos/Neg" value={`${scoreBoard.positiveTrades}/${scoreBoard.negativeTrades}`} />
          <ScoreCard title="Win Rate" value={`${scoreBoard.winRate}%`} />
          <ScoreCard title="Growth" value={`${scoreBoard.growth}%`} type={scoreBoard.growth >= 0 ? "positive" : "negative"} />
          <ScoreCard title="Balance" value={`$${scoreBoard.balance.toLocaleString()}`} type={scoreBoard.balance >= 0 ? "positive" : "negative"} />
        </div>

        {/* Open Trades */}
        <Card className="mb-8 bg-white shadow-sm">
          <CardHeader className="bg-blue-100 py-2">
            <CardTitle className="text-lg font-semibold text-blue-900">Open Trades</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow className="bg-blue-50">
                  <TableHead className="font-semibold text-xs">ID</TableHead>
                  <TableHead className="font-semibold text-xs">Symbol</TableHead>
                  <TableHead className="font-semibold text-xs">Buy Price</TableHead>
                  <TableHead className="font-semibold text-xs">SL</TableHead>
                  <TableHead className="font-semibold text-xs">Target</TableHead>
                  <TableHead className="font-semibold text-xs">Buy DateTime</TableHead>
                  <TableHead className="font-semibold text-xs">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {openTrades.map((trade) => (
                  <TableRow key={trade.id} className="hover:bg-blue-50">
                    <TableCell className="text-sm">{trade.id}</TableCell>
                    <TableCell className="text-sm font-medium">{trade.symbol}</TableCell>
                    <TableCell className="text-sm">{trade.buyPrice}</TableCell>
                    <TableCell className="text-sm">{trade.sl}</TableCell>
                    <TableCell className="text-sm">{trade.target}</TableCell>
                    <TableCell className="text-sm">{trade.buyDateTime}</TableCell>
                    <TableCell className="text-sm">{trade.status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Closed Trades */}
        <Card className="bg-white shadow-sm">
          <CardHeader className="bg-blue-100 py-2">
            <CardTitle className="text-lg font-semibold text-blue-900">Closed Trades</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow className="bg-blue-50">
                  <TableHead className="font-semibold text-xs">ID</TableHead>
                  <TableHead className="font-semibold text-xs">Symbol</TableHead>
                  <TableHead className="font-semibold text-xs">Buy Price</TableHead>
                  <TableHead className="font-semibold text-xs">Sell Price</TableHead>
                  <TableHead className="font-semibold text-xs">Buy DateTime</TableHead>
                  <TableHead className="font-semibold text-xs">Sell DateTime</TableHead>
                  <TableHead className="font-semibold text-xs">Quantity</TableHead>
                  <TableHead className="font-semibold text-xs">PNL</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {closedTrades.map((trade) => (
                  <TableRow key={trade.id} className="hover:bg-blue-50">
                    <TableCell className="text-sm">{trade.id}</TableCell>
                    <TableCell className="text-sm font-medium">{trade.symbol}</TableCell>
                    <TableCell className="text-sm">{trade.buyPrice}</TableCell>
                    <TableCell className="text-sm">{trade.sellPrice}</TableCell>
                    <TableCell className="text-sm">{trade.buyDateTime}</TableCell>
                    <TableCell className="text-sm">{trade.sellDateTime}</TableCell>
                    <TableCell className="text-sm">{trade.quantity}</TableCell>
                    <TableCell className={`text-sm font-semibold ${trade.pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                      {trade.pnl}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function ScoreCard({ title, value, type = "neutral" }) {
  return (
    <Card className="bg-white shadow-sm transition-all duration-300 hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-1">
        <CardTitle className="text-sm font-medium text-blue-900">{title}</CardTitle>
        {type === "positive" && <ArrowUpIcon className="h-4 w-4 text-green-600" />}
        {type === "negative" && <ArrowDownIcon className="h-4 w-4 text-red-600" />}
      </CardHeader>
      <CardContent>
        <div className={`text-xl font-bold ${type === "positive" ? "text-green-600" : type === "negative" ? "text-red-600" : "text-blue-900"}`}>
          {value}
        </div>
      </CardContent>
    </Card>
  )
}