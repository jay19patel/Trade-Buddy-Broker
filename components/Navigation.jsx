'use client'
import Cookies from 'js-cookie'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { VscListFlat } from 'react-icons/vsc'
import { GrAnalytics } from 'react-icons/gr'
import { SiManageiq } from 'react-icons/si'
import { BiLogOut } from 'react-icons/bi'
import { TbTransactionDollar } from 'react-icons/tb'
import { ImAddressBook } from "react-icons/im";
import { cn } from '@/lib/utils'
import { LuContact } from "react-icons/lu";

const menuItems = [
  { name: 'Dashboard', url: '/', icon: GrAnalytics },
  // { name: 'Overview', url: '/trades-overview', icon: VscGitPullRequestCreate },
  { name: 'Create Order', url: '/create-order', icon: SiManageiq },
  { name: 'Transaction', url: '/transaction', icon: TbTransactionDollar },
  { name: 'Position Book', url: '/positionbook', icon: ImAddressBook },
  { name: 'Contact Us', url: '/hello-world', icon: LuContact },
  { name: 'Logout', url: '/logout', icon: BiLogOut },
]

const MenuItem = ({ item, onClick, mobile = false }) => (
  <li className={cn(
    'hover:bg-white rounded-sm px-2 py-3 text-white hover:text-black hover:font-bold',
    mobile && 'text-lg'
  )}>
    <Link href={item.url} onClick={() => onClick(item.name)} className="flex items-center gap-5">
      <item.icon className="pl-2" size={30} />
      {item.name}
    </Link>
  </li>
)

const Sidebar = ({ mobile = false, onMenuItemClick }) => (
  <div className={cn(
    'flex flex-col h-full',
    mobile ? 'w-full' : 'bg-blue-950 shadow-xl'
  )}>
    <div className="h-20 flex items-center justify-center font-extrabold text-white tracking-tighter text-4xl">
      Trade Buddy
    </div>
    <nav className="flex-1 pl-10 w-[90%]">
      <ul className="flex flex-col gap-2">
        {menuItems.map((item, index) => (
          <MenuItem key={index} item={item} onClick={onMenuItemClick} mobile={mobile} />
        ))}
      </ul>
    </nav>
  </div>
)

const Footer = () => (
  <footer className="bg-gray-100 text-gray-600 py-4 px-6">
    <div className="container mx-auto flex flex-wrap justify-between items-center">
      <div className="w-full md:w-1/3 text-center md:text-left">
        <p>&copy; 2023 Trade Buddy. All rights reserved.</p>
      </div>
    </div>
  </footer>
)

export default function NavigatoionBarLayout({ children }) {
  const router = useRouter()
  const [currentPage, setCurrentPage] = useState('Dashboard') // Default to "Dashboard" or pass it as a prop
  const full_name = Cookies.get("full_name")

  const handleMenuItemClick = (name) => {
    setCurrentPage(name); // Update currentPage state
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="hidden md:block w-64 flex-shrink-0">
        <Sidebar onMenuItemClick={handleMenuItemClick} />
      </aside>
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-xl h-12 flex items-center justify-between px-5">
          <div className="flex items-center gap-5">
            <Sheet>
              <SheetTrigger className="md:hidden">
                <VscListFlat size={30} />
              </SheetTrigger>
              <SheetContent side="left" className="p-0 w-[300px] bg-blue-950">
                <Sidebar mobile onMenuItemClick={handleMenuItemClick} />
              </SheetContent>
            </Sheet>
            <h1 className="text-xl font-bold">{currentPage}</h1>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger>Hey {full_name}</DropdownMenuTrigger>
            {/* Uncomment and modify if needed
            <DropdownMenuContent className="bg-white">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => router.push('/profile')}>Profile</DropdownMenuItem>
              <DropdownMenuItem onClick={() => router.push('/reset_password')}>Reset Password</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="bg-red-100" onClick={() => router.push('/logout')}>Logout</DropdownMenuItem>
            </DropdownMenuContent> */}
          </DropdownMenu>
        </header>
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  )
}
