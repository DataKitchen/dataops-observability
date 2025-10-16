#!/bin/sh

/usr/bin/envsubst <<EOT > /observability_ui/shell/environments/environment.json
{
  "apiBaseUrl": "${OBSERVABILITY_API_BASE_URL:-/api}"
}
EOT

cat <<EOT > /observability_ui/shell/assets/module-federation.manifest.json
{
  "basic-auth": {
    "routePath": "authentication",
    "remoteEntry": "/auth/remoteEntry.js",
    "remoteName": "basic-auth",
    "exposedModule": "./Authentication",
    "exposedModuleName": "AuthenticationModule"
  }
}
EOT
