import { ElementRef } from '@angular/core';
import { fakeAsync, tick } from '@angular/core/testing';
import { TruncateDirective } from './truncate.directive';

describe('truncate directive', () => {
  let directive: TruncateDirective;
  let element: ElementRef;
  let resizeCallback: ResizeObserverCallback;

  class MockedResizeObserver {
    constructor(callback: ResizeObserverCallback) {
      resizeCallback = callback;
    }

    // eslint-disable-next-line @typescript-eslint/no-empty-function
    observe() {}
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    unobserve() {}
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    disconnect() {}
  }

  beforeEach(async () => {
    element = { nativeElement: { style: {}, classList: { add: jest.fn(), remove: jest.fn() }, getBoundingClientRect: jest.fn() } } as ElementRef;

    global.ResizeObserver = MockedResizeObserver;
    directive = new TruncateDirective(element);
  });

  it('should create', () => {
    expect(directive).toBeTruthy();
  });

  it('should add truncated css class when subject is true', fakeAsync(() => {
    directive.truncated.next(true);
    tick();
    expect(element.nativeElement.classList.add).toBeCalledWith('truncated');
  }));

  it('should remove truncated css class when subject is false', fakeAsync(() => {
    directive.truncated.next(true);
    tick();
    directive.truncated.next(false);
    tick();
    expect(element.nativeElement.classList.remove).toBeCalledWith('truncated');
  }));

  it('should set trunncated true if the element width is overflowed', fakeAsync(() => {
    element.nativeElement.clientWidth = 100;
    element.nativeElement.scrollWidth = 110;

    resizeCallback([], new ResizeObserver(() => undefined));
    tick();

    expect(directive.truncated.getValue()).toBeTruthy();
  }));

  it('should set trunncated true if the element height is overflowed', fakeAsync(() => {
    element.nativeElement.clientHeight = 100;
    element.nativeElement.scrollHeight = 110;

    resizeCallback([], new ResizeObserver(() => undefined));
    tick();

    expect(directive.truncated.getValue()).toBeTruthy();
  }));

  it('should set trunncated false if the element is not overflowed', fakeAsync(() => {
    element.nativeElement.clientWidth = 100;
    element.nativeElement.scrollWidth = 90;
    element.nativeElement.clientHeight = 100;
    element.nativeElement.scrollHeight = 90;

    resizeCallback([], new ResizeObserver(() => undefined));
    tick();

    expect(directive.truncated.getValue()).toBeFalsy();
  }));

  describe('ngOnInit', () => {
    it('should set required style for element to truncate text', () => {
      directive.ngOnInit();

      expect(element.nativeElement.style.maxWidth).toBe('100%');
      expect(element.nativeElement.style.wordBreak).toBe('break-all');
      expect(element.nativeElement.style.whiteSpace).toBe('nowrap');
    });
  });

  describe('ngOnDestroy', () => {
    it('should unsubscribe from all subscriptions', () => {
      directive.subscriptions = [{ unsubscribe: jest.fn() }, { unsubscribe: jest.fn() }, { unsubscribe: jest.fn() }] as any[];
      directive.ngOnDestroy();

      expect(directive.subscriptions.map(s => (s.unsubscribe as any).mock.calls.length)).toEqual([ 1, 1, 1 ]);
    });
  });
});
