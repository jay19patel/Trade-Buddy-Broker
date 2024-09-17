import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ArrowDownIcon, ArrowUpIcon, PlusIcon } from "lucide-react";

const DashbordCount = () => {
  const DashbordConts = [
    {
      title: "Total Counts",
      counts: 100,
    },
    {
      title: "Total Counts",
      counts: 100,
    },
    {
      title: "Total Counts",
      counts: -10,
    },
    {
      title: "Total Counts",
      counts: 100,
    },
  ];
  return (
    <div>
      <div className="grid grid-cols-2 gap-5 md:grid-cols-4 py-5">
        {DashbordConts.map((dashbordcard, index) => (
          <Card
            className="w-full max-w-sm bg-white border-[#d0d0d0] shadow-lg"
            key={index}
          >
            <CardContent className="p-6 flex flex-col items-center justify-center gap-4">
              <div className="flex flex-col items-center">
                <h2 className="text-lg  text-[#747474]">
                  {dashbordcard.title}
                </h2>
                <span
                  className={`text-xl font-bold flex justify-center items-center gap-2 ${
                    dashbordcard.counts > 0
                      ? "text-green-600"
                      : dashbordcard.counts < 0
                      ? "text-red-600"
                      : "text-blue-900"
                  }`}
                >
                  {dashbordcard.counts > 0 ? (
                    <ArrowUpIcon className="h-4 w-4 text-green-600" />
                  ) : dashbordcard.counts < 0 ? (
                    <ArrowDownIcon className="h-4 w-4 text-red-600" />
                  ) : null}
                  {dashbordcard.counts}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default DashbordCount;
