import { listEnvVariableFormatter } from './tools.utilities';

describe('listEnvVariableFormatter', () => {
  it('should generate list value correctly for script', () => {
    const testCases = [
      { input: '', output: '[]' },
      { input: null, output: '[]' },
      { input: '   ', output: '[]' },
      { input: 'pip', output: '[\\"pip\\"]' },
      { input: 'pip1,pip2', output: '[\\"pip1\\",\\"pip2\\"]' },
      { input: '  pip1  ,  pip2  ', output: '[\\"pip1\\",\\"pip2\\"]' },
    ];
    testCases.forEach(({ input, output }) => {
      expect(listEnvVariableFormatter(input)).toEqual(output);
    });
  });
});
