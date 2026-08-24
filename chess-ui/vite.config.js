import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'


const EMPTY_REACT_DEVTOOLS_SOURCE_MAP = JSON.stringify({
  version: 3,
  file: 'installHook.js',
  sources: ['installHook.js'],
  sourcesContent: [''],
  names: [],
  mappings: '',
})


function reactDevToolsSourceMapFallback() {
  return {
    name: 'ccc-react-devtools-source-map-fallback',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const requestPath = request.url?.split('?', 1)[0] ?? ''
        const isSourceMapRequest = requestPath.endsWith('/installHook.js.map')
        const isSupportedMethod = request.method === 'GET' || request.method === 'HEAD'

        if (!isSourceMapRequest || !isSupportedMethod) {
          next()
          return
        }

        response.statusCode = 200
        response.setHeader('Content-Type', 'application/json; charset=utf-8')
        response.setHeader('Cache-Control', 'no-store')
        response.end(request.method === 'HEAD' ? undefined : EMPTY_REACT_DEVTOOLS_SOURCE_MAP)
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [reactDevToolsSourceMapFallback(), react()],
})
