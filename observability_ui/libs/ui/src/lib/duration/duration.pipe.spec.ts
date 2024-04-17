import { TestBed } from '@angular/core/testing';
import { DurationPipe } from './duration.pipe';

describe('Duration Pipe', () => {
  const start = new Date(Date.UTC(2022, 5, 15, 13, 0, 10, 27384));
  const end = new Date(Date.UTC(2022, 5, 15, 18, 15, 10, 27384));

  let pipe: DurationPipe;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        DurationPipe,
      ]
    });

    pipe = TestBed.inject(DurationPipe);
  });

  it('should return formatted hours and minutes for date values', () => {
    const value = pipe.transform(start, end);
    expect(value).toBe('5h 15m');
  });

  it('should default to zero seconds when start and end are the same', () => {
    const startDate = new Date(Date.UTC(2022, 5, 15, 13, 0, 10, 27384));
    const endDate = new Date(Date.UTC(2022, 5, 15, 13, 0, 10, 27384));

    const value = pipe.transform(startDate, endDate);
    expect(value).toBe('0s');
  });

  it('should return formatted hours and minutes for string values', () => {
    const value = pipe.transform('2022-07-08T13:48:05', '2022-07-08T15:48:05');
    expect(value).toBe('2h');
  });

  it('should return empty string if start is undefined', () => {
    const value = pipe.transform(null as any, '2022-07-08T13:48:05');
    expect(value).toBe('');
  });

  it('should return empty string if end is undefined', () => {
    const value = pipe.transform('2022-07-08T13:48:05', null as any);
    expect(value).toBe('');
  });

  it('should return formatted minutes and seconds if hours value is 0', () => {
    const startDate = new Date(Date.UTC(2022, 5, 15, 13, 0, 10, 27384));
    const endDate = new Date(Date.UTC(2022, 5, 15, 13, 15, 13, 27384));

    const value = pipe.transform(startDate, endDate);
    expect(value).toBe('15m 3s');
  });

  it('should include days', () => {
    const startDate = new Date(Date.UTC(2023, 4, 1, 13, 0, 10, 27384));
    const endDate = new Date(Date.UTC(2023, 4, 15, 14, 0, 10, 27384));

    const value = pipe.transform(startDate, endDate);
    expect(value).toBe('14d 1h');
  });

  it('should limit to the 2 biggest units', () => {
    const startDate = new Date(Date.UTC(2023, 4, 1, 13, 0, 10, 27384));
    const endDate = new Date(Date.UTC(2023, 4, 15, 13, 20, 30, 27384));

    const value = pipe.transform(startDate, endDate);
    expect(value).toBe('14d 20m');
  });

  it('should return a fixed value when exceeding the cap', () => {
    const startDate = new Date(Date.UTC(2012, 5, 1, 13, 0, 10, 27384));
    const endDate = new Date(Date.UTC(2022, 5, 15, 13, 15, 13, 27384));

    const value = pipe.transform(startDate, endDate);
    expect(value).toBe('1000d+');
  });
});
