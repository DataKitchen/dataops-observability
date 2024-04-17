import { TestBed } from '@angular/core/testing';
import { SchedulePipe } from './schedule.pipe';

import { Schedule } from '@observability-ui/core';

describe('Schedule Pipe', () => {
  const schedule: Schedule = { schedule: '0 1 */2 * *', timezone: 'America/New_York' } as Schedule;

  let pipe: SchedulePipe;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ SchedulePipe ],
    });

    pipe = TestBed.inject(SchedulePipe);
  });

  it('should guard against failsy schedule', () => {
    const value = pipe.transform(null);
    expect(value).toBe('...');
  });

  it('should guard against empty schedule expression', () => {
    const value = pipe.transform({ ...schedule, schedule: '' });
    expect(value).toBe('...');
  });

  it('should guard against null schedule expression', () => {
    const value = pipe.transform({ ...schedule, schedule: null as any });
    expect(value).toBe('...');
  });

  it('should guard against undefined schedule expression', () => {
    const value = pipe.transform({ ...schedule, schedule: undefined as any });
    expect(value).toBe('...');
  });

  it('should render a readable description', () => {
    const value = pipe.transform(schedule);
    expect(value).toBe('01:00 am, every 2 days (America/New_York)');
  });

  it('should render a readable description without the timezone', () => {
    const value = pipe.transform({ ...schedule, timezone: undefined });
    expect(value).toBe('01:00 am, every 2 days');
  });
});
