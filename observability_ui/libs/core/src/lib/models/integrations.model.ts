export interface IntegrationV1 {
  integration_name: 'TESTGEN';
}

export interface TestgenTestOutcomeIntegrationV1 extends IntegrationV1 {
  integration_name: 'TESTGEN';
  table: string;
  columns?: string[];
  test_suite: string;
  version: number;
  test_parameters: Parameter[];
}

interface Parameter {
  name: string;
  value: string | number;
}
