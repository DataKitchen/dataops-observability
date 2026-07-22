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

# Generate the nginx listener config (included by nginx.conf)
if [ -n "$SSL_CERT_FILE" ] && [ -n "$SSL_KEY_FILE" ] && [ -f "$SSL_CERT_FILE" ] && [ -f "$SSL_KEY_FILE" ]; then
  cat <<EOT > /etc/nginx/conf.d/listen.conf
listen       8082 ssl;
listen  [::]:8082 ssl;
ssl_certificate     $SSL_CERT_FILE;
ssl_certificate_key $SSL_KEY_FILE;
EOT
else
  cat <<EOT > /etc/nginx/conf.d/listen.conf
listen       8082;
listen  [::]:8082;
EOT
fi
