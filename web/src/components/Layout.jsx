import { useState, useEffect, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'

export default function Layout({ children, theme, setTheme, onLogout }) {
  const qc = useQueryClient()
  const [lastRefresh, setLastRefresh] = useState(new Date())
  const [elapsed, setElapsed] = useState(0)

  const refresh = useCallback(() => {
    qc.invalidateQueries()
    setLastRefresh(new Date())
    setElapsed(0)
  }, [qc])

  // Compteur de secondes depuis le dernier refresh
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((new Date() - lastRefresh) / 1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [lastRefresh])

  // Détecter les refreshs automatiques de React Query
  useEffect(() => {
    const unsubscribe = qc.getQueryCache().subscribe(event => {
      if (event?.type === 'updated' && event?.action?.type === 'success') {
        setLastRefresh(new Date())
        setElapsed(0)
      }
    })
    return () => unsubscribe()
  }, [qc])

  const formatElapsed = (s) => {
    if (s < 60)  return `${s}s`
    if (s < 3600) return `${Math.floor(s / 60)}min`
    return `${Math.floor(s / 3600)}h`
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.reload()
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏊</span>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">DeepPool</h1>
          </div>
          <div className="flex items-center gap-3">

            {/* Refresh + elapsed */}
            <div className="flex items-center gap-2">
              <button
                onClick={refresh}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-lg"
                title="Rafraîchir les données"
              >
                🔄
              </button>
              <span className="text-xs text-gray-400 dark:text-gray-500 min-w-[3rem]">
                il y a {formatElapsed(elapsed)}
              </span>
            </div>

            {/* Theme toggle */}
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-lg"
              title="Changer le thème"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>

            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-red-500 dark:hover:text-red-400 transition-colors"
            >
              Déconnexion
            </button>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-6">
        {children}
      </main>
    </div>
  )
}