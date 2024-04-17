import { TestBed } from '@angular/core/testing';
import { TimespanPipe } from './timespan.pipe';

describe('Duration Pipe', () => {
  let pipe: TimespanPipe;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        TimespanPipe,
      ]
    });

    pipe = TestBed.inject(TimespanPipe);
  });

  it('should return days', () => {
    const value = pipe.transform(86400 * 2);
    expect(value).toBe('2 days');
  });

  it('should return hours', () => {
    const value = pipe.transform(3600);
    expect(value).toBe('1 hours');
  });

  it('should return minutes', () => {
    const value = pipe.transform(30);
    expect(value).toBe('0.5 minutes');
  });
});
