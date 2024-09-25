
"use client"
import Cookies from 'js-cookie'; 
import { Divide } from "lucide-react";
import DashbordCount from "./dashbordCount";
import OpenPositionsTable from "./dashbordOpenPositions"
import ClosePositionsTable from "./dashbordClosePositions";
import { useState, useEffect } from 'react'
import { useToast } from "@/hooks/use-toast"

export default function Dashboard() {

  const { toast } = useToast()
  const [openTrades, setOpenTrades] = useState([])
  const [closeTrades, setCloseTrades] = useState([])
  const [dashBordCount, setDashBordCount] = useState([
    {
      title: "Total Position",
      counts: 0,
    },
    {
      title: "Open/Close",
      counts: 0,
    },
    {
      title: "Positive/Negative",
      counts: 0,
    },
    // {
    //   title: "P&L Realized",
    //   counts: 0,
    // },
    {
      title: "Total P&N",
      counts: 0,
    },
    
  ])
  const [isLoading, setIsLoading] = useState(true)
  const fetchTrades = async () => {
    setIsLoading(true)
    try {
      // const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBY2NvdW50SWQiOiJLSDJZRCIsIkFjY291bnRFbWFpbCI6ImpheUBnbWFpbC5jb20iLCJBY2NvdW50Um9sZSI6IlVzZXIiLCJleHAiOjIwMzgxNjk5MzQsImp0aSI6IjJiZmEzOWEyLTA0MzMtNDRjYS1hNzlkLTdlM2IyY2ViZDdmNyJ9.78GtirKl3kyHqXmEk_Ntt6FILGUnVVaogbZydD26nRY";
      // console.log("Cooookies is :",Cookies.get("access_token"))
      const token  = Cookies.get("access_token")

      const response = await fetch('http://127.0.0.1:8080/order/positions?trade_today=true', {
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
      const OpenPositionList = data.data.filter((n) => n.position_status === "Pending")
      const ClosePositionList = data.data.filter((n) => n.position_status === "Completed")
      setOpenTrades(OpenPositionList)
      setCloseTrades(ClosePositionList)
      const DashbordConts = [
        {
          title: "Total Position",
          counts: data.overview.total_positions,
        },
        {
          title: "Open/Close",
          counts: `${data.overview.open_positions}/${data.overview.closed_positions}`,
        },
        {
          title: "Positive/Negative",
          counts: `${data.overview.positive_pnl_count}/${data.overview.negative_pnl_count}`,
        },
        // {
        //   title: "P&L Realized",
        //   counts: data.overview.pnl_realized,
        // },
        {
          title: "Total P&N",
          counts: data.overview.pnl_total,
        },
        
      ];

      setDashBordCount(DashbordConts)

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


  return (

    <div>
      <DashbordCount DashbordConts={dashBordCount}/>
      <OpenPositionsTable  isLoading={isLoading} trades={openTrades} />
      <ClosePositionsTable  isLoading={isLoading} trades={closeTrades} />
    </div>
  )
}