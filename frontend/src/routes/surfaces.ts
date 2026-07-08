// The five operations surfaces named in issue #50. Navigation placeholders in
// this chunk; each gets a real screen in a later chunk.

export interface Surface {
  path: string
  label: string
}

export const SURFACES: Surface[] = [
  { path: '/dashboards', label: 'Dashboards' },
  { path: '/project-setup', label: 'Project setup' },
  { path: '/worker-tasks', label: 'Worker tasks' },
  { path: '/tasks', label: 'Task queue' },
  { path: '/review', label: 'Review queue' },
]
