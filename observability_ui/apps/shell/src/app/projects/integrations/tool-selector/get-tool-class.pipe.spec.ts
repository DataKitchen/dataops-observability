import { TestBed } from '@angular/core/testing';
import { GetToolClassPipe } from './get-tool-class.pipe';
import { EXTRA_TOOL_ICONS, INTEGRATION_TOOLS } from '../integrations.model';

describe('get-tool-class', () => {

  class A {
    static _name = 'A';
  }

  class B {
    static _name = 'B';
  }

  const C = {_name: 'c', _displayName: 'C', _icon: 'c'};

  let pipe: GetToolClassPipe;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        GetToolClassPipe,
        {
          provide: INTEGRATION_TOOLS,
          useValue: [A, B],
        },
        {
          provide: EXTRA_TOOL_ICONS,
          useValue: [ C ],
        },
      ],
    });

    pipe = TestBed.inject(GetToolClassPipe);

  });

  it('should create', () => {
    expect(pipe).toBeTruthy();
  });

  it('should get class by `_name`', () => {
    expect(pipe.transform('A')).toEqual(A);
  });

  it('should get object from the extra tool icons token', () => {
    expect(pipe.transform('C')).toEqual(C);
  });

  it('should be defensive', () => {
    expect(pipe.transform(undefined)).toBeUndefined();
  });
});
