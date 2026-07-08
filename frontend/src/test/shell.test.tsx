import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../App'

function renderApp(path = '/tasks') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  )
}

describe('App shell', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the wordmark and the five navigation placeholders', () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => new Promise<Response>(() => {}))
    renderApp()

    expect(screen.getByText('Workstream')).toBeInTheDocument()
    const nav = screen.getByRole('navigation', { name: /primary/i })
    for (const label of [
      'Project setup',
      'Task queue',
      'Worker tasks',
      'Review queue',
      'Dashboards',
    ]) {
      expect(within(nav).getByText(label)).toBeInTheDocument()
    }
  })

  it('renders backend health and a signed-out actor when unauthenticated', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      const url = String(input)
      if (url.endsWith('/health')) {
        return Promise.resolve(new Response(JSON.stringify({ status: 'ok' }), { status: 200 }))
      }
      return Promise.resolve(
        new Response(JSON.stringify({ detail: 'Missing bearer token' }), { status: 401 }),
      )
    })
    renderApp()

    expect(await screen.findByText('ok')).toBeInTheDocument()
    expect((await screen.findAllByText('signed out')).length).toBeGreaterThan(0)
  })

  it('renders the authenticated actor name and roles', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      const url = String(input)
      if (url.endsWith('/health')) {
        return Promise.resolve(new Response(JSON.stringify({ status: 'ok' }), { status: 200 }))
      }
      return Promise.resolve(
        new Response(
          JSON.stringify({
            actor_id: 'a1',
            external_subject: 'sub',
            external_issuer: 'iss',
            email: null,
            display_name: 'Research Lead',
            roles: ['reviewer'],
            auth_source: 'dev_mock',
            is_dev_auth: true,
            audit_context: {
              actor_id: 'a1',
              external_subject: 'sub',
              external_issuer: 'iss',
              actor_roles: ['reviewer'],
              claim_snapshot: {},
              auth_source: 'dev_mock',
              is_dev_auth: true,
            },
          }),
          { status: 200 },
        ),
      )
    })
    renderApp()

    expect(await screen.findByText(/· reviewer/)).toBeInTheDocument()
    expect(screen.getAllByText(/Research Lead/).length).toBeGreaterThan(0)
  })

  it('shows an unreachable API state when health fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      const url = String(input)
      if (url.endsWith('/health')) {
        return Promise.reject(new Error('network down'))
      }
      return Promise.resolve(
        new Response(JSON.stringify({ detail: 'Missing bearer token' }), { status: 401 }),
      )
    })
    renderApp()

    expect(await screen.findByText('unreachable')).toBeInTheDocument()
  })

  it('renders a not-found message for an unknown route', () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => new Promise<Response>(() => {}))
    renderApp('/does-not-exist')

    expect(screen.getByText('Not found')).toBeInTheDocument()
  })
})
