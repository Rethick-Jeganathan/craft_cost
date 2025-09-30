export const metadata = {
  title: 'craft_cost',
  description: 'Spend better. Simple financial clarity.',
}

import './globals.css'
import Link from 'next/link'
import Image from 'next/image'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen`}>
        <header className="border-b border-[var(--border)]/60 bg-[var(--surface)]/60 backdrop-blur">
          <nav className="container flex items-center justify-between py-3">
            <Link href="/" className="flex items-center gap-2 text-sm font-semibold">
              <Image src="/logo.svg" alt="craft_cost" width={16} height={16} className="opacity-90" />
              craft_cost
            </Link>
            <div className="flex items-center gap-4 text-sm text-[var(--muted)]">
              <Link href="/" className="hover:text-white">Home</Link>
              <Link href="/upload" className="hover:text-white">Upload CSV</Link>
              <Link href="/spend" className="hover:text-white">Spend</Link>
              <Link href="/flags" className="hover:text-white">Flags</Link>
            </div>
          </nav>
        </header>
        <main className="container py-8">
          {children}
        </main>
      </body>
    </html>
  )
}
