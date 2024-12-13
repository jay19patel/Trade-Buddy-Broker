import localFont from "next/font/local";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import ClientLayout from "@/components/ClientLayout"; // Import ClientLayout

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata = {
  title: "Trade Buddy Paper Broker",
  description: "Development by Jay Patel",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gradient-to-br from-blue-900 to-green-900`}
      >
        <ClientLayout>{children}</ClientLayout>  {/* Wrap children in ClientLayout */}
        <Toaster />
      </body>
    </html>
  );
}
