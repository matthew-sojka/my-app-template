import { queryOptions } from '@tanstack/react-query'
import { apiGet } from './client'

// Mirrors the backend's HealthResponse. Hand-written for now; Phase 3 generates
// these types from the OpenAPI schema.
export interface HealthResponse {
  status: 'ok' | 'degraded'
  environment: string
  database: 'ok' | 'unavailable'
}

export const healthQueryOptions = queryOptions({
  queryKey: ['health'],
  queryFn: ({ signal }) => apiGet<HealthResponse>('/api/health', signal),
  refetchInterval: 30_000,
})
