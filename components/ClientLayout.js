'use client';

import { usePathname } from 'next/navigation';
import NavigationBarLayout from "@/components/Navigation";

export default function ClientLayout({ children }) {
  const pathname = usePathname();
  const isSpecialPage = pathname === '/accounts' || pathname === '/tickets';

  return (
    <>
      {isSpecialPage ? (
        <div className="simple-layout">{children}</div> 
      ) : (
        <NavigationBarLayout>{children}</NavigationBarLayout>
      )}
    </>
  );
}
