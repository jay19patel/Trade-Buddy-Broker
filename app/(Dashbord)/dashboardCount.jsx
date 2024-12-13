import React from "react";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { ArrowDownIcon, ArrowUpIcon } from "lucide-react";


const DashboardCount = ({ DashboardCounts }) => {
  if (!Array.isArray(DashboardCounts)) {
    console.error("DashboardCounts is not an array:", DashboardCounts);
    return null;
  }

  return (
    <div className="grid grid-cols-2 gap-5 md:grid-cols-3 py-5">
      {DashboardCounts.map((dashboardCard, index) => (
        <Card
          key={index}
          className="w-full max-w-sm bg-white border-[#d0d0d0] shadow-lg"
        >
          <CardContent className="p-6 flex flex-col items-center justify-center gap-4">
            <div className="flex flex-col items-center">
              <h2 className="text-lg text-[#747474] font-semibold">
                {dashboardCard.title}
              </h2>
              <span
                className={`text-xl font-bold flex justify-center items-center gap-2 ${
                  typeof dashboardCard.counts === 'number'
                    ? dashboardCard.counts > 0
                      ? "text-green-600"
                      : dashboardCard.counts < 0
                      ? "text-red-600"
                      : "text-blue-900"
                    : "text-blue-900"
                }`}
              >
                {typeof dashboardCard.counts === 'number' && (
                  dashboardCard.counts > 0 ? (
                    <ArrowUpIcon className="h-4 w-4 text-green-600" />
                  ) : dashboardCard.counts < 0 ? (
                    <ArrowDownIcon className="h-4 w-4 text-red-600" />
                  ) : null
                )}
                {dashboardCard.counts}
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default DashboardCount;