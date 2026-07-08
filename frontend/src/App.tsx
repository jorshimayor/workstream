import { Navigate, Route, Routes } from 'react-router-dom'
import { getCurrentActor } from './api/auth'
import { getHealth } from './api/health'
import { useAsync } from './api/useAsync'
import { BackendStatus } from './components/BackendStatus'
import { NavShell } from './components/NavShell'
import { NotFound } from './routes/NotFound'
import { Placeholder } from './routes/Placeholder'
import { SURFACES } from './routes/surfaces'

export default function App() {
  const health = useAsync(getHealth)
  const actor = useAsync(getCurrentActor)

  return (
    <div className="app">
      <NavShell actor={actor} />
      <BackendStatus health={health} actor={actor} />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/tasks" replace />} />
          {SURFACES.map((surface) => (
            <Route
              key={surface.path}
              path={surface.path}
              element={<Placeholder title={surface.label} />}
            />
          ))}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  )
}
