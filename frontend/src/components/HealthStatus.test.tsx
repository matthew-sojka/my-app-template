import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { HealthResponse } from '../api/health'
import { renderWithQueryClient } from '../test/render'
import { HealthStatus } from './HealthStatus'

function mockFetch(status: number, body: unknown) {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  )
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('HealthStatus', () => {
  it('shows a pending state while loading', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {}))) // never resolves

    renderWithQueryClient(<HealthStatus />)

    expect(screen.getByRole('status')).toHaveTextContent('Checking API…')
  })

  it('shows ok when the API and database are healthy', async () => {
    const healthy: HealthResponse = { status: 'ok', environment: 'local', database: 'ok' }
    const fetchMock = mockFetch(200, healthy)

    renderWithQueryClient(<HealthStatus />)

    expect(await screen.findByText('API ok · local · database ok')).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/health', expect.anything())
  })

  it('shows degraded when the API returns 503 because the database is down', async () => {
    const degraded: HealthResponse = {
      status: 'degraded',
      environment: 'local',
      database: 'unavailable',
    }
    mockFetch(503, degraded)

    renderWithQueryClient(<HealthStatus />)

    expect(
      await screen.findByText('API degraded · local · database unavailable'),
    ).toBeInTheDocument()
  })

  it('shows unreachable when the request fails entirely', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    renderWithQueryClient(<HealthStatus />)

    expect(await screen.findByText('API unreachable (Failed to fetch)')).toBeInTheDocument()
  })
})
