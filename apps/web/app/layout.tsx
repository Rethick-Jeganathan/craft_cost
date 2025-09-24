export const metadata = {
  title: 'Debt & Expense Reduction Advisor',
  description: 'MVP web app',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'system-ui, sans-serif', margin: 0 }}>
        {children}
      </body>
    </html>
  )
}
