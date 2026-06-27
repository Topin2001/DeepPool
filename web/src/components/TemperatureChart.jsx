import { useState } from 'react'

const TIME_RANGES = [
  { label: '12h',  value: 'now-12h'  },
  { label: '24h', value: 'now-24h' },
  { label: '2j',  value: 'now-2d'  },
  { label: '3j',  value: 'now-3d'  },
  { label: '7j',  value: 'now-7d'  },
]

export default function TemperatureChart({ theme }) {
  const [range, setRange] = useState('now-2d')

  const grafanaTheme = theme === 'dark' ? 'dark' : 'light'
  const src = `/grafana/d-solo/adm5m65/suivi-piscine?orgId=1&panelId=panel-1&from=${range}&to=now&timezone=browser&refresh=30s&theme=${grafanaTheme}`

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Température & Pompe
        </h2>
        <div className="flex gap-1">
          {TIME_RANGES.map(r => (
            <button
              key={r.value}
              onClick={() => setRange(r.value)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                range === r.value
                  ? 'bg-pool-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>
      <iframe
        key={`${grafanaTheme}-${range}`}
        src={src}
        width="100%"
        height="400"
        frameBorder="0"
        title="Grafana — Température piscine"
        className="block"
      />
    </div>
  )
}