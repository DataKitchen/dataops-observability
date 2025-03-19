import { TestBed } from '@angular/core/testing';
import { ParseDatePipe } from './parseDate.pipe';
import * as parseDate from '@observability-ui/core';

jest.mock('@observability-ui/core', () => {
  return {
    __esModule: true,
    ...jest.requireActual('@observability-ui/core')
  };
});

describe('parseDate.pipe', () => {
  let pipe: ParseDatePipe;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [ ParseDatePipe ],
    }).compileComponents();

    pipe = TestBed.inject(ParseDatePipe);
  });

  it('should create', () => {
    expect(pipe).toBeTruthy();
  });

  describe('transform', () => {
    it('should call parseDate', () => {
      const spy = jest.spyOn(parseDate, 'parseDate');
      pipe.transform('test');

      expect(spy).toHaveBeenCalledWith('test');
    });
  });
});
