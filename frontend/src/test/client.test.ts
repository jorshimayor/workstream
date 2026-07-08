import { ApiError, apiFetch } from '../api/client'

describe('apiFetch', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    window.localStorage.clear()
  })

  it('attaches a bearer token and parses JSON', async () => {
    window.localStorage.setItem('workstream_token', 'dev-token')
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(new Response(JSON.stringify({ status: 'ok' }), { status: 200 }))

    const data = await apiFetch<{ status: string }>('/health')

    expect(data).toEqual({ status: 'ok' })
    // The path is prefixed with the /api/v1 base — the connectivity contract.
    expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/v1/health')
    const init = fetchMock.mock.calls[0]?.[1]
    const headers = new Headers(init?.headers)
    expect(headers.get('Authorization')).toBe('Bearer dev-token')
  })

  it('sends no Authorization header when no token is present', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(new Response(JSON.stringify({ status: 'ok' }), { status: 200 }))

    await apiFetch('/health')

    const init = fetchMock.mock.calls[0]?.[1]
    const headers = new Headers(init?.headers)
    expect(headers.has('Authorization')).toBe(false)
  })

  it('throws a typed ApiError with status and detail on non-2xx', async () => {
    // Return a fresh Response per call: a response body can only be read once.
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(() =>
      Promise.resolve(
        new Response(JSON.stringify({ detail: 'Missing bearer token' }), { status: 401 }),
      ),
    )

    const error = await apiFetch('/auth/me').catch((caught: unknown) => caught)

    expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/v1/auth/me')
    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 401, detail: 'Missing bearer token' })
  })
})
