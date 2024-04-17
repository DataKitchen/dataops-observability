import { TestBed } from '@angular/core/testing';
import { NullifyPendingPipe } from './nullify-pending.pipe';

describe('nullify-pending', () => {

  let pipe: NullifyPendingPipe;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ NullifyPendingPipe ],
    });

    pipe = TestBed.inject(NullifyPendingPipe);
  });

  it('should exists', () => {
    expect(pipe).toBeTruthy();
  });

  it('should be transparent to all types', () => {
    expect(pipe.transform(1)).toEqual(1);
    expect(pipe.transform(true)).toEqual(true);
    expect(pipe.transform({a: '1'})).toEqual({a: '1'});
    expect(pipe.transform('1')).toEqual('1');
  });

  it('should return null if string starts with _DK_PENDING', () => {
    expect(pipe.transform('_DK_PENDING_anything')).toBeNull();
    expect(pipe.transform('_DK_PENDING_')).toBeNull();
  });

});
