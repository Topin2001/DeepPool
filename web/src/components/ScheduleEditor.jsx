import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getSchedule, updateSchedule } from '../api/client'

const DEFAULT_SLOT = {
  start: '08:00',
  end: '12:00',
  min_temp: null,
  extensions: []
}

const DEFAULT_EXTENSION = { above: 28.0, extend_after_minutes: 60 }

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

  const addSlot = () => setSlots([...slots, { ...DEFAULT_SLOT, extensions: [] }])
  const removeSlot = i => setSlots(slots.filter((_, idx) => idx !== i))

  const updateSlot = (i, field, value) => {
    const updated = [...slots]
    updated[i] = { ...updated[i], [field]: value }
    setSlots(updated)
  }

  const addExtension = i => {
    const updated = [...slots]
    updated[i] = { ...updated[i], extensions: [...updated[i].extensions, { ...DEFAULT_EXTENSION }] }
    setSlots(updated)
  }

  const removeExtension = (i, j) => {
    const updated = [...slots]
    updated[i] = { ...updated[i], extensions: updated[i].extensions.filter((_, idx) => idx !== j) }
    setSlots(updated)
  }

  const updateExtension = (i, j, field, value) => {
    const updated = [...slots]
    const exts = [...updated[i].extensions]
    exts[j] = { ...exts[j], [field]: value }
    updated[i] = { ...updated[i], extensions: exts }
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
        <div className="space-y-4">
          {slots.map((slot, i) => (
            <div key={i} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-xl space-y-3">

              {/* Horaires */}
              <div className="flex items-center gap-3 flex-wrap">
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
                <button
                  onClick={() => removeSlot(i)}
                  className="ml-auto text-red-400 hover:text-red-600 transition-colors text-lg px-2"
                  title="Supprimer la plage"
                >
                  ×
                </button>
              </div>

              {/* Température minimale d'activation */}
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-500 dark:text-gray-400">Activer seulement si temp &gt;</span>
                <input
                  type="number"
                  step="0.5"
                  placeholder="—"
                  value={slot.min_temp ?? ''}
                  onChange={e => updateSlot(i, 'min_temp', e.target.value === '' ? null : parseFloat(e.target.value))}
                  className="w-20 px-2 py-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-pool-500"
                />
                <span className="text-sm text-gray-500 dark:text-gray-400">°C (vide = toujours)</span>
              </div>

              {/* Extensions */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Extensions après la plage</span>
                  <button
                    onClick={() => addExtension(i)}
                    className="text-xs px-2 py-1 bg-pool-500 hover:bg-pool-600 text-white rounded-lg transition-colors"
                  >
                    + Ajouter
                  </button>
                </div>

                {slot.extensions.length === 0 ? (
                  <p className="text-xs text-gray-400">Aucune extension</p>
                ) : (
                  slot.extensions.map((ext, j) => (
                    <div key={j} className="flex items-center gap-2 flex-wrap bg-white dark:bg-gray-600 rounded-lg px-3 py-2">
                      <span className="text-xs text-gray-500 dark:text-gray-400">Si temp &gt;</span>
                      <input
                        type="number"
                        step="0.5"
                        value={ext.above}
                        onChange={e => updateExtension(i, j, 'above', parseFloat(e.target.value))}
                        className="w-16 px-2 py-1 rounded-lg border border-gray-300 dark:border-gray-500 bg-gray-50 dark:bg-gray-700 text-xs focus:outline-none focus:ring-2 focus:ring-pool-500"
                      />
                      <span className="text-xs text-gray-500 dark:text-gray-400">°C → prolonger de</span>
                      <input
                        type="number"
                        step="5"
                        value={ext.extend_after_minutes}
                        onChange={e => updateExtension(i, j, 'extend_after_minutes', parseInt(e.target.value))}
                        className="w-16 px-2 py-1 rounded-lg border border-gray-300 dark:border-gray-500 bg-gray-50 dark:bg-gray-700 text-xs focus:outline-none focus:ring-2 focus:ring-pool-500"
                      />
                      <span className="text-xs text-gray-500 dark:text-gray-400">min</span>
                      <button
                        onClick={() => removeExtension(i, j)}
                        className="ml-auto text-red-400 hover:text-red-600 transition-colors"
                        title="Supprimer"
                      >
                        ×
                      </button>
                    </div>
                  ))
                )}
              </div>

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