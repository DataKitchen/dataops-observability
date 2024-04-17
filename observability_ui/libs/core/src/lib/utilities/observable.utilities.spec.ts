import { of } from 'rxjs';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { max, min } from './observable.utilities';

describe('observable.utilities', () => {
  describe('min()', () => {
    it('should return the minimum value from an observable of array', () => {
      new TestScheduler().expect$(of([ 3, 7, 1, 8, 9 ]).pipe(min())).toBe('(a|)', {a: 1});
    });

    it('should start with a default value in case of empty arrays', () => {
      new TestScheduler().expect$(of([]).pipe(min((x, y) => x - y, () => 0))).toBe('(a|)', {a: 0});
    });

    it('should ignore the default value if the array is not empty', () => {
      new TestScheduler().expect$(of([ 3, 7, -1 ]).pipe(min((x, y) => x - y, () => 0))).toBe('(a|)', {a: -1});
    });

    it('should compare complex objects', () => {
      const expected = {start: 2, end: 3};
      new TestScheduler().expect$(of([
        {start: 4, end: 6},
        {start: 7, end: 10},
        {start: 2, end: 3},
      ]).pipe(min((x, y) => x.start - y.start))).toBe('(a|)', {a: expected});
    });
  });

  describe('max()', () => {
    it('should return the maximum value from an observable of array', () => {
      new TestScheduler().expect$(of([ 3, 7, 1, 8, 9 ]).pipe(max())).toBe('(a|)', {a: 9});
    });

    it('should start with a default value in case of empty arrays', () => {
      new TestScheduler().expect$(of([]).pipe(max((x, y) => x - y, () => 15))).toBe('(a|)', {a: 15});
    });

    it('should ignore the default value if the array is not empty', () => {
      new TestScheduler().expect$(of([ 3, 7, -1 ]).pipe(max((x, y) => x - y, () => 0))).toBe('(a|)', {a: 7});
    });

    it('should compare complex objects', () => {
      const expected = {start: 7, end: 10};
      new TestScheduler().expect$(of([
        {start: 4, end: 6},
        {start: 7, end: 10},
        {start: 2, end: 3},
      ]).pipe(max((x, y) => x.end - y.end))).toBe('(a|)', {a: expected});
    });
  });
});
