import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getOverride, updateOverride } from '../api/client'

export default function PumpControl() {
  const qc = useQueryClient()
  const { data } = useQuery({ queryKey: ['override'], queryFn: getOverride })

  const mutation = useMutation({
    mutationFn: updateOverride,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['override'] })
      qc.invalidateQueries({ queryKey: ['status'] })
    }
  })

  const current = data?.state  // true | false | null

  const buttons = [
    { label: 'Marche forcée', value: true,  color: 'green' },
    { label: 'Auto',          value: null,  color: 'blue'  },
    { label: 'Arrêt forcé',   value: false, color: 'red'   },
  ]

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Contrôle pompe</h2>
      <div className="flex flex-col gap-2">
        {buttons.map(btn => {
          const isActive = current === btn.value
          const styles = {
            green: isActive
              ? 'bg-green-500 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-green-900/20',
            blue: isActive
              ? 'bg-pool-500 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-pool-50 dark:hover:bg-pool-900/20',
            red: isActive
              ? 'bg-red-500 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20',
          }
          return (
            <button
              key={String(btn.value)}
              onClick={() => mutation.mutate(btn.value)}
              disabled={isActive || mutation.isPending}
              className={`py-2 px-4 rounded-lg font-medium transition-colors ${styles[btn.color]} disabled:opacity-60`}
            >
              {btn.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}