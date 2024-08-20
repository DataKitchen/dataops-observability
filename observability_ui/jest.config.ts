const { getJestProjects } = require('@nx/jest');

export default {
  projects: getJestProjects(),

  coverageDirectory: 'coverage',
  reporters: [
    'default',
    ['jest-junit', { outputDirectory: 'coverage', outputName: 'junit.xml' }],
  ],
  coverageReporters: ['html', 'lcov', 'text', 'cobertura'],
  collectCoverageFrom: [
    'src/(app|lib)/**/*.ts',
    '!src/(app|lib)/**/*.module.ts',
    '!src/(app|lib)/**/*.translation(|s).ts',
    '!src/(app|lib)/**/entry.component.ts',
    '!src/(app|lib)/**/*.model.ts',
    '!src/(app|lib)/**/*.mock.ts',
    '!src/(app|lib)/**/index.ts',
    '!src/app/projects/analytics/**/*.ts',
  ],
  coverageThreshold: {
    global: {
      statements: 89.25,
      branches: 68.65,
      functions: 78.46,
      lines: 90.25,
    },
  }
};
