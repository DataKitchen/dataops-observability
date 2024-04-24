module.exports = {
  ci: {
    collect: {
      url: [],
    },
    assert: {
      preset: 'lighthouse:recommended',
      assertions: {
        'robots-txt': 'off',
        'uses-long-cache-ttl': 'off',
        'legacy-javascript': 'warn',

        'max-potential-fid': 'off',
        'interactive': ['warn', {minScore: 0.4}],
        'unused-javascript': 'off',
        'unused-css-rules': 'off',

        'service-worker': 'off',

        'csp-xss': 'off',
        'non-composited-animations': 'off',
        'speed-index': ['warn', {minScore: 0.8}],
        'server-response-time': 'off',
        'mainthread-work-breakdown': 'off',
        'bootup-time': ['warn', {minScore: 0.7}]
      }
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
