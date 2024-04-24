import { TestBed } from '@angular/core/testing';
import { GetIngrationPipe } from './get-integration.pipe';
import { IntegrationV1 } from '@observability-ui/core';

describe('Get Ingration Pipe', () => {
  let pipe: GetIngrationPipe;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        GetIngrationPipe,
      ]
    });

    pipe = TestBed.inject(GetIngrationPipe);
  });

  it('should create', () => {
    expect(pipe).toBeTruthy();
  });

  it('should return undefined if no integrations', () => {
    expect(pipe.transform(undefined as any, 'TESTGEN')).toEqual(undefined);
  });

  it('should return undefined if integrations array is empty', () => {
    expect(pipe.transform([], 'TESTGEN')).toEqual(undefined);
  });

  it('should return undefined if name is not given', () => {
    expect(pipe.transform([], '' as any)).toEqual(undefined);
  });

  it('should return undefined for invalid names', () => {
    expect(pipe.transform([ {integration_name: 'TESTGEN'} ], 'INVALID' as any)).toEqual(undefined);
  });

  it('should return the integration matching the provided name', () => {
    const integration = {integration_name: 'TESTGEN'} as IntegrationV1;
    expect(pipe.transform([integration], 'TESTGEN')).toEqual(integration);
  });
});
