/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_WORKSTREAM_TOKEN?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
