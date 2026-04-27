import Layout from '../components/Layout'
import StatusBanner from '../components/StatusBanner'
import TemperatureChart from '../components/TemperatureChart'
import PumpControl from '../components/PumpControl'
import TempSettings from '../components/TempSettings'
import ScheduleEditor from '../components/ScheduleEditor'
import TodaySchedule from '../components/TodaySchedule'

export default function Dashboard({ theme, setTheme, onLogout }) {
  return (
    <Layout theme={theme} setTheme={setTheme} onLogout={onLogout}>
      <div className="space-y-6">
        <StatusBanner />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <TemperatureChart />
          </div>
          <div className="space-y-6">
            <PumpControl />
            <TempSettings />
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ScheduleEditor />
          </div>
          <div>
            <TodaySchedule />
          </div>
        </div>
      </div>
    </Layout>
  )
}