import { IsTodayPipe } from './is-today.pipe';
import { TestBed } from '@angular/core/testing';

describe('Is Today Pipe', () => {
  let pipe: IsTodayPipe;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        IsTodayPipe
      ]
    });

    pipe = TestBed.inject(IsTodayPipe);
  });

  it('should return true if date is today', () => {
    const dateToCheck = new Date();
    expect(pipe.transform(dateToCheck)).toBeTruthy();
  });

  it('should return false if date is not today', () => {
    const dateToCheck = new Date();
    dateToCheck.setDate(new Date().getDate() + 1);
    expect(pipe.transform(dateToCheck)).toBeFalsy();
  });
});
