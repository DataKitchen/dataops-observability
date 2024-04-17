import { EventType } from '@observability-ui/core';
import { TestBed } from '@angular/core/testing';
import { OperationPipe } from './operation.pipe';

describe('Operation Pipe', () => {
  const events: EventType[] = [
    { raw_data: { operation: 'WRITE' } } as EventType,
    { raw_data: { operation: 'READ' } } as EventType,
    { raw_data: { operation: 'READ' } } as EventType
  ];

  let pipe: OperationPipe;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        OperationPipe,
      ]
    });

    pipe = TestBed.inject(OperationPipe);
  });

  it('should filter the array based on operation', () => {
    expect(pipe.transform(events, 'READ').length).toEqual(2);
    expect(pipe.transform(events, 'WRITE').length).toEqual(1);
  });
});
