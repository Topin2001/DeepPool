import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getSchedule, updateSchedule } from '../api/client'

export default function ScheduleEditor() {
  const qc = useQueryClient()
  const { data } = useQuery({ queryKey: ['schedule'], queryFn: getSchedule })
  const [slots, setSlots] = useState([])
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (data?.schedule) setSlots(data.schedule)
  }, [data])

  const mutation = useMutation({
    mutationFn: updateSchedule,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['schedule'] })
      setSuccess(true)
      setTimeout(() => setSuccess(false), 2000)
    }
  })

  const addSlot = () => setSlots([...slots, { start: '08:00', end: '12:00', temp_extensions: [] }])

  const removeSlot = i => setSlots(slots.filter((_, idx) => idx !== i))

  const updateSlot = (i, field, value) => {
    const updated = [...slots]
    updated[i] = { ...updated[i], [field]: value }
    setSlots(updated)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Planning</h2>
        <button
          onClick={addSlot}
          className="px-3 py-1.5 text-sm bg-pool-500 hover:bg-pool-600 text-white rounded-lg transition-colors"
        >
          + Ajouter une plage
        </button>
      </div>

      {slots.length === 0 ? (
        <p className="text-gray-400 text-sm text-center py-6">
          Aucune plage — la température décide seule.
        </p>
      ) : (
        <div className="space-y-3">
          {slots.map((slot, i) => (
            <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
              <div className="flex items-center gap-2 flex-1">
                <span className="text-sm text-gray-500 dark:text-gray-400">De</span>
                <input
                  type="time"
                  value={slot.start}
                  onChange={e => updateSlot(i, 'start', e.target.value)}
                  className="px-2 py-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-pool-500"
                />
                <span className="text-sm text-gray-500 dark:text-gray-400">à</span>
                <input
                  type="time"
                  value={slot.end}
                  onChange={e => updateSlot(i, 'end', e.target.value)}
                  className="px-2 py-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-pool-500"
                />
              </div>
              <button
                onClick={() => removeSlot(i)}
                className="text-red-400 hover:text-red-600 transition-colors text-lg px-2"
                title="Supprimer"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={() => mutation.mutate(slots)}
          disabled={mutation.isPending}
          className="px-6 py-2 bg-pool-500 hover:bg-pool-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {mutation.isPending ? 'Sauvegarde...' : 'Sauvegarder le planning'}
        </button>
        {success && <span className="text-green-500 text-sm">✓ Sauvegardé</span>}
      </div>
    </div>
  )
}