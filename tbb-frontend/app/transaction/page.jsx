"use client";

import { useState, useEffect } from "react";
import { v4 as uuidv4 } from 'uuid';
import { PlusIcon, ArrowUpCircleIcon, ArrowDownCircleIcon, DollarSignIcon, ClipboardIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";

export default function Component() {
  const [transactions, setTransactions] = useState([]);
  const [transactionType, setTransactionType] = useState("Deposit");
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");
  const [balance, setBalance] = useState(0);

  useEffect(() => {
    if (transactions.length > 0) {
      setBalance(transactions[transactions.length - 1].balance);
    }
  }, [transactions]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const newBalance = transactionType === "Deposit" 
      ? balance + parseFloat(amount) 
      : balance - parseFloat(amount);
    const newTransaction = {
      transaction_id: uuidv4(),
      account_id: "ACC" + Math.floor(1000 + Math.random() * 9000).toString(),
      transaction_type: transactionType,
      transaction_amount: parseFloat(amount),
      transaction_note: note,
      balance: newBalance,
    };
    setTransactions([...transactions, newTransaction]);
    setAmount("");
    setNote("");
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <Card className="mb-8 bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg">
        <CardHeader>
          <CardTitle className="text-center text-3xl font-bold">Current Balance</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-5xl font-bold flex items-center justify-center">
            <DollarSignIcon className="mr-2 h-8 w-8" />
            ₹{balance.toFixed(2)}
          </p>
        </CardContent>
      </Card>

      <Card className="mb-8 shadow-md bg-white">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Add Transaction</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="type" className="text-sm font-medium">Transaction Type</Label>
              <RadioGroup
                id="type"
                value={transactionType}
                onValueChange={(value) => setTransactionType(value)}
                className="flex space-x-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="Deposit" id="deposit" />
                  <Label htmlFor="deposit" className="text-sm">Deposit</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="Withdraw" id="withdraw" />
                  <Label htmlFor="withdraw" className="text-sm">Withdraw</Label>
                </div>
              </RadioGroup>
            </div>
            <div className="space-y-2">
              <Label htmlFor="amount" className="text-sm font-medium">Amount</Label>
              <Input
                id="amount"
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Enter amount"
                required
                className="w-full"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="note" className="text-sm font-medium">Note</Label>
              <Textarea
                id="note"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Enter transaction note"
                className="w-full"
              />
            </div>
            <Button type="submit" size="sm" className="w-full bg-blue-800 hover:bg-blue-600 text-white">
              <PlusIcon className="mr-2 h-4 w-4" /> Submit Transaction
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="shadow-md bg-white">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Transaction History</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">ID</TableHead>
                <TableHead>Account</TableHead>
                <TableHead>Type</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Note</TableHead>
                <TableHead className="text-right">Balance</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((transaction) => (
                <TableRow
                  key={transaction.transaction_id}
                  className={
                    transaction.transaction_type === "Deposit"
                      ? "bg-green-50"
                      : "bg-red-50"
                  }
                >
                  <TableCell className="font-medium">{transaction.transaction_id.slice(0, 8)}</TableCell>
                  <TableCell>{transaction.account_id}</TableCell>
                  <TableCell className="flex items-center">
                    {transaction.transaction_type === "Deposit" 
                      ? <ArrowUpCircleIcon className="mr-2 h-4 w-4 text-green-500" />
                      : <ArrowDownCircleIcon className="mr-2 h-4 w-4 text-red-500" />
                    }
                    {transaction.transaction_type}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    ₹{transaction.transaction_amount.toFixed(2)}
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate" title={transaction.transaction_note || '-'}>
                    {transaction.transaction_note?.trim() === "" ? "-" : transaction.transaction_note}
                    </TableCell>

                  <TableCell className="text-right font-semibold">
                    ₹{transaction.balance.toFixed(2)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
