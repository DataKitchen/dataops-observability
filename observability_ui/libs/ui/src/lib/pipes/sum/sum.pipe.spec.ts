import { TestBed } from '@angular/core/testing';
import { SumPipe } from './sum.pipe';

describe('sum.pipe', () => {
  let pipe: SumPipe;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [ SumPipe ],
    }).compileComponents();

    pipe = TestBed.inject(SumPipe);
  });

  it('should create', () => {
    expect(pipe).toBeTruthy();
  });

  describe('transform', () => {
    it('should sum array of numbers', () => {
      expect(pipe.transform([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])).toBe(55);
    });

    it('should sum array of objects using the key function', () => {
      expect(pipe.transform([
        {status: 'A', count: 10},
        {status: 'B', count: 3},
        {status: 'C', count: 5},
      ], 'count')).toBe(18);
    });
  });
});
