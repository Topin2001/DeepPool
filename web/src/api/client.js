import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const client = axios.create({ baseURL: API_URL })

client.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const login = async (username, password) => {
  const form = new FormData()
  form.append('username', username)
  form.append('password', password)
  const res = await client.post('/auth/login', form)
  localStorage.setItem('token', res.data.access_token)
}

export const getStatus        = () => client.get('/status').then(r => r.data)
export const getTemperature   = (hours = 24) => client.get('/temperature', { params: { hours } }).then(r => r.data)
export const getPumpHistory   = (hours = 24) => client.get('/pump/history', { params: { hours } }).then(r => r.data)
export const getConfig        = () => client.get('/config').then(r => r.data)
export const getSchedule      = () => client.get('/schedule').then(r => r.data)
export const getScheduleToday = () => client.get('/schedule/today').then(r => r.data)
export const getOverride      = () => client.get('/override').then(r => r.data)

export const updateConfig   = (data)     => client.put('/config', data).then(r => r.data)
export const updateOverride = (state)    => client.put('/override', { state }).then(r => r.data)
export const updateSchedule = (schedule) => client.put('/schedule', { schedule }).then(r => r.data)