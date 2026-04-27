import { useQuery } from '@tanstack/react-query'
import { getScheduleToday } from '../api/client'

export default function TodaySchedule() {
  const { data, isLoading } = useQuery({
    queryKey: ['scheduleToday'],
    queryFn: getScheduleToday,
  })

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Aujourd'hui
      </h2>

      {isLoading ? (
        <p className="text-gray-400 text-sm">Chargement...</p>
      ) : (
        <>
          {/* Température moyenne J-1 */}
          <div className="flex items-center gap-3 mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
            <span className="text-2xl">🌡️</span>
            <div>
              <div className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                Température moyenne hier
              </div>
              <div className="text-xl font-bold text-blue-700 dark:text-blue-300">
                {data?.avg_temp_yesterday != null
                  ? `${data.avg_temp_yesterday} °C`
                  : 'Données insuffisantes'}
              </div>
            </div>
          </div>

          {/* Plages prévues */}
          <div className="space-y-2">
            <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              Fonctionnement prévu
            </div>
            {data?.planned_slots?.length === 0 ? (
              <p className="text-gray-400 text-sm">Aucune plage configurée</p>
            ) : (
              data?.planned_slots?.map((slot, i) => (
                <div
                  key={i}
                  className={`flex items-center justify-between px-4 py-2 rounded-lg text-sm font-medium
                    ${slot.activated
                      ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-400 line-through'
                    }`}
                >
                  <span>🕐 {slot.start} → {slot.end}</span>
                  <span className="text-xs">
                    {!slot.activated && 'Temp. insuffisante'}
                    {slot.activated && slot.extended && '⏱ Étendue'}
                    {slot.activated && !slot.extended && '✓'}
                  </span>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}