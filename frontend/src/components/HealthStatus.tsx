import { useQuery } from '@tanstack/react-query'
import { ApiError } from '../api/client'
import { healthQueryOptions, type HealthResponse } from '../api/health'
import './HealthStatus.css'

export function HealthStatus() {
  const { data, error, isPending } = useQuery(healthQueryOptions)

  // A 503 still carries a HealthResponse body saying which part is down.
  const health: HealthResponse | undefined =
    data ??
    (error instanceof ApiError && error.status === 503
      ? (error.body as HealthResponse)
      : undefined)

  let state: 'pending' | 'ok' | 'error'
  let label: string
  if (isPending) {
    state = 'pending'
    label = 'Checking API…'
  } else if (health) {
    state = health.status === 'ok' ? 'ok' : 'error'
    label = `API ${health.status} · ${health.environment} · database ${health.database}`
  } else {
    state = 'error'
    label = `API unreachable (${error?.message})`
  }

  return (
    <div className={`health-status health-status--${state}`} role="status">
      <span className="health-status__dot" aria-hidden="true" />
      {label}
    </div>
  )
}
