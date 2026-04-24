import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getConfig, updateConfig } from '../api/client'

export default function TempSettings() {
  const qc = useQueryClient()
  const { data } = useQuery({ queryKey: ['config'], queryFn: getConfig })

  const [tempOn,  setTempOn]  = useState('')
  const [tempOff, setTempOff] = useState('')
  const [error,   setError]   = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (data) {
      setTempOn(data.temp_on)
      setTempOff(data.temp_off)
    }
  }, [data])

  const mutation = useMutation({
    mutationFn: updateConfig,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['config'] })
      setSuccess(true)
      setTimeout(() => setSuccess(false), 2000)
    },
    onError: err => setError(err.response?.data?.detail || 'Erreur')
  })

  const handleSubmit = () => {
    setError('')
    const on  = parseFloat(tempOn)
    const off = parseFloat(tempOff)
    if (isNaN(on) || isNaN(off)) return setError('Valeurs invalides')
    if (off >= on) return setError('Arrêt doit être inférieur à Démarrage')
    mutation.mutate({ temp_on: on, temp_off: off })
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Températures</h2>
      <div className="space-y-3">
        <div>
          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">Démarrage (°C)</label>
          <input
            type="number"
            step="0.5"
            value={tempOn}
            onChange={e => setTempOn(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-pool-500"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">Arrêt (°C)</label>
          <input
            type="number"
            step="0.5"
            value={tempOff}
            onChange={e => setTempOff(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-pool-500"
          />
        </div>
        {error   && <p className="text-red-500 text-sm">{error}</p>}
        {success && <p className="text-green-500 text-sm">✓ Sauvegardé</p>}
        <button
          onClick={handleSubmit}
          disabled={mutation.isPending}
          className="w-full py-2 bg-pool-500 hover:bg-pool-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {mutation.isPending ? 'Sauvegarde...' : 'Sauvegarder'}
        </button>
      </div>
    </div>
  )
}