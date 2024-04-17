import { TestBed } from '@angular/core/testing';
import { HumanizePipe } from './humanize.pipe';

describe('Humanize Pipe', () => {
  let pipe: HumanizePipe;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        HumanizePipe,
      ]
    });

    pipe = TestBed.inject(HumanizePipe);
  });

  it('should create', () => {
    expect(pipe).toBeTruthy();
  });

  it('should return an empty string if value is an empty string', () => {
    expect(pipe.transform('')).toEqual('');
  });

  it('should return an empty string if value is undefined', () => {
    expect(pipe.transform(undefined as any)).toEqual('');
  });

  it('should return an empty string if value is null', () => {
    expect(pipe.transform(null as any)).toEqual('');
  });

  it('should remove all underscores from the value', () => {
    expect(pipe.transform('my_slug_string')).toEqual('my slug string');
  });

  it('should remove all hyphens from the value', () => {
    expect(pipe.transform('my_slug_string-extra')).toEqual('my slug string extra');
  });
});
