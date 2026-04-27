import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { getTemperature, getPumpHistory } from '../api/client'

const RANGES = [
  { label: '6 h',  hours: 6   },
  { label: '12 h', hours: 12  },
  { label: '24 h', hours: 24  },
  { label: '2 j',  hours: 48  },
  { label: '3 j',  hours: 72  },
  { label: '7 j',  hours: 168 },
]

function formatTime(isoString, hours) {
  const d = new Date(isoString)
  if (hours <= 24) {
    return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('fr-FR', { weekday: 'short', hour: '2-digit', minute: '2-digit' })
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  const temp = payload.find(p => p.dataKey === 'temp')
  const pump = payload.find(p => p.dataKey === 'pump')
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl px-3 py-2 text-sm shadow-lg">
      <p className="text-gray-400 text-xs mb-1">{label}</p>
      {temp && (
        <p className="text-sky-400 font-medium">{temp.value} °C</p>
      )}
      {pump !== undefined && (
        <p className={pump?.value ? 'text-emerald-400' : 'text-gray-500'}>
          Pompe {pump?.value ? 'ON' : 'OFF'}
        </p>
      )}
    </div>
  )
}

export default function TemperatureChart() {
  const [hours, setHours] = useState(24)

  const { data: tempData, isLoading: loadingTemp } = useQuery({
    queryKey: ['temperature', hours],
    queryFn: () => getTemperature(hours),
    staleTime: 60_000,
  })

  const { data: pumpData, isLoading: loadingPump } = useQuery({
    queryKey: ['pump-history', hours],
    queryFn: () => getPumpHistory(hours),
    staleTime: 60_000,
  })

  const chartData = useMemo(() => {
    if (!tempData?.data) return []

    const allTimes = new Map()

    for (const t of tempData.data) {
      const key = new Date(t.time).toISOString()
      if (!allTimes.has(key)) allTimes.set(key, { time: t.time })
      allTimes.get(key).temp = t.value
    }

    if (pumpData?.data) {
      for (const p of pumpData.data) {
        const key = new Date(p.time).toISOString()
        if (!allTimes.has(key)) allTimes.set(key, { time: p.time })
        allTimes.get(key).pump = p.value
      }
    }

    return Array.from(allTimes.values())
      .sort((a, b) => new Date(a.time) - new Date(b.time))
      .map(d => ({ ...d, label: formatTime(d.time, hours) }))
  }, [tempData, pumpData, hours])

  const isLoading = loadingTemp || loadingPump

  const temps = chartData.map(d => d.temp).filter(v => v != null)
  const minTemp = temps.length ? Math.floor(Math.min(...temps)) - 1 : 20
  const maxTemp = temps.length ? Math.ceil(Math.max(...temps)) + 1 : 35

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-5 gap-4 flex-wrap">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Température &amp; pompe
        </h2>

        {/* Sélecteur de plage */}
        <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700 rounded-xl p-1">
          {RANGES.map(r => (
            <button
              key={r.hours}
              onClick={() => setHours(r.hours)}
              className={[
                'px-3 py-1 rounded-lg text-sm font-medium transition-all duration-150',
                hours === r.hours
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200',
              ].join(' ')}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* Légende */}
      <div className="flex items-center gap-5 mb-4 text-xs text-gray-500 dark:text-gray-400">
        <span className="flex items-center gap-1.5">
          <span className="inline-block w-6 h-0.5 bg-sky-400 rounded" />
          Température (°C)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 rounded-sm bg-emerald-400 opacity-70" />
          Pompe active
        </span>
      </div>

      {/* Graphique */}
      {isLoading ? (
        <div className="h-72 flex items-center justify-center text-gray-400">Chargement…</div>
      ) : chartData.length === 0 ? (
        <div className="h-72 flex items-center justify-center text-gray-400">Aucune donnée</div>
      ) : (
        <ResponsiveContainer width="100%" height={288}>
          <ComposedChart data={chartData} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" strokeOpacity={0.5} />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              interval="preserveStartEnd"
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              yAxisId="temp"
              domain={[minTemp, maxTemp]}
              tick={{ fontSize: 11, fill: '#38bdf8' }}
              unit="°C"
              tickLine={false}
              axisLine={false}
              width={44}
            />
            <YAxis
              yAxisId="pump"
              orientation="right"
              domain={[0, 1]}
              hide
            />
            <Tooltip content={<CustomTooltip />} />
            {/* Barres pompe en arrière-plan */}
            <Bar
              yAxisId="pump"
              dataKey="pump"
              fill="#34d399"
              opacity={0.25}
              radius={[2, 2, 0, 0]}
              maxBarSize={12}
            />
            {/* Courbe température au premier plan */}
            <Line
              yAxisId="temp"
              type="monotone"
              dataKey="temp"
              stroke="#38bdf8"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 0 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}