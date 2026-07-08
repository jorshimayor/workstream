interface PlaceholderProps {
  title: string
}

export function Placeholder({ title }: PlaceholderProps) {
  return (
    <section>
      <p className="section-label">Operations surface</p>
      <h1 className="display-title">{title}</h1>
      <p className="body-copy">
        This surface is a navigation placeholder. Its screen is implemented in a later chunk of
        the frontend initiative.
      </p>
    </section>
  )
}
