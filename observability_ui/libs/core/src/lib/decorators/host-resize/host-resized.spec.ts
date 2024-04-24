import { Component, OnInit } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { OnHostResized } from './host-resize';

describe('OnHostResized', () => {
  const updateFn = jest.fn();
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

  global.ResizeObserver = MockedResizeObserver;

  @Component({
    selector: 'test',
    template: `<h1>test component</h1>`
  })
  class TestComponent implements OnInit {
    element = { nativeElement: { getBoundingClientRect: jest.fn() } };

    ngOnInit(): void { void 1; }

    @OnHostResized()
    update(): void {
      updateFn();
    }
  }

  @Component({
    selector: 'test-2',
    template: `<h1>test component</h1>`
  })
  class Test2Component {
    element = { nativeElement: { getBoundingClientRect: jest.fn() } };

    @OnHostResized()
    update(): void {
      updateFn();
    }
  }

  @Component({
    selector: 'test-3',
    template: `<h1>test component</h1>`
  })
  class Test3Component {
    element = { nativeElement: { getBoundingClientRect: jest.fn() } };

    @OnHostResized('elm')
    update(): void {
      updateFn();
    }
  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        TestComponent,
        Test2Component,
      ],
    });


    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeDefined();
  });

  it('should call the decorated method when the component resizes', () => {
    resizeCallback([], new ResizeObserver(() => undefined));
    expect(updateFn).toBeCalledTimes(1);
  });

  describe('component without given lifecycle hook', () => {

    it('should create', () => {
      const fixture = TestBed.createComponent(Test2Component);
      fixture.detectChanges();

      expect(fixture.componentInstance).toBeTruthy();
    });
  });

  describe('component with wrong element name', () => {

    let fix: ComponentFixture<Test3Component>;

    beforeEach(() => {

      jest.spyOn(console, 'warn').mockImplementation();

      fix = TestBed.createComponent(Test3Component);

      fix.detectChanges();

    });

    it('should create', () => {
      expect(fix.componentInstance).toBeTruthy();
    });

    it('should warn', () => {
      expect(console.warn).toHaveBeenCalled();
    });
  });
});
