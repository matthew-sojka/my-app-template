import '@testing-library/jest-dom/vitest' // adds matchers like toHaveTextContent
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

afterEach(() => {
  cleanup() // unmount rendered components between tests
  vi.unstubAllGlobals() // undo vi.stubGlobal('fetch', ...)
})
