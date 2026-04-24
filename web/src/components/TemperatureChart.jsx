import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { getTemperature } from '../api/client'

export default function TemperatureChart() {
  const { data, isLoading } = useQuery({
    queryKey: ['temperature'],
    queryFn: getTemperature,
  })

  const chartData = data?.data?.map(d => ({
    time: new Date(d.time).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
    temp: d.value
  })) || []

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Température — 24 dernières heures
      </h2>
      {isLoading ? (
        <div className="h-64 flex items-center justify-center text-gray-400">Chargement...</div>
      ) : chartData.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-400">Aucune donnée</div>
      ) : (
        <ResponsiveContainer width="100%" height={264}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={['auto', 'auto']}
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              unit="°C"
            />
            <Tooltip
              formatter={v => [`${v} °C`, 'Température']}
              contentStyle={{
                backgroundColor: '#1f2937',
                border: 'none',
                borderRadius: '8px',
                color: '#f9fafb'
              }}
            />
            <Line
              type="monotone"
              dataKey="temp"
              stroke="#0ea5e9"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}