import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

export default function App() {
  const [theme, setTheme] = useState(() =>
    localStorage.getItem('theme') || 'light'
  )

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('theme', theme)
  }, [theme])

  const token = localStorage.getItem('token')

  return (
    <div className={theme}>
      {token
        ? <Dashboard theme={theme} setTheme={setTheme} />
        : <Login />
      }
    </div>
  )
}