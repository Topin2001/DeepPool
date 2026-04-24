import { useQuery } from '@tanstack/react-query'
import { getStatus } from '../api/client'

export default function StatusBanner() {
  const { data, isLoading } = useQuery({
    queryKey: ['status'],
    queryFn: getStatus,
  })

  const pumpOn = data?.pump
  const override = data?.override

  let modeLabel = 'Auto'
  if (override === true)  modeLabel = 'Forcé ON'
  if (override === false) modeLabel = 'Forcé OFF'

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <Card
        label="Température"
        value={isLoading ? '...' : data?.temperature != null ? `${data.temperature.toFixed(1)} °C` : 'N/A'}
        icon="🌡️"
        color="blue"
      />
      <Card
        label="Pompe"
        value={isLoading ? '...' : pumpOn ? 'En marche' : 'Arrêtée'}
        icon={pumpOn ? '💧' : '⏸️'}
        color={pumpOn ? 'green' : 'gray'}
      />
      <Card
        label="Mode"
        value={isLoading ? '...' : modeLabel}
        icon="⚙️"
        color="purple"
      />
    </div>
  )
}

function Card({ label, value, icon, color }) {
  const colors = {
    blue:   'bg-blue-50   dark:bg-blue-900/20  text-blue-600   dark:text-blue-400',
    green:  'bg-green-50  dark:bg-green-900/20 text-green-600  dark:text-green-400',
    gray:   'bg-gray-50   dark:bg-gray-700     text-gray-600   dark:text-gray-300',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
  }

  return (
    <div className={`rounded-2xl p-5 ${colors[color]}`}>
      <div className="text-3xl mb-2">{icon}</div>
      <div className="text-sm font-medium opacity-70">{label}</div>
      <div className="text-2xl font-bold mt-1">{value}</div>
    </div>
  )
}