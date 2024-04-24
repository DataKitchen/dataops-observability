import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DynamicComponentOutletDirective } from './dynamic-component-outlet.directive';
import { Component, Input } from '@angular/core';

describe('dynamic-component-outlet', () => {

  @Component({
    selector: 'dynamic-component',
    template: `
          <h1>{{label}}</h1>
      `
  })
  class DynamicComponent {
    @Input() label!: string;
  }

  @Component({
    selector: 'test-component',
    template: `
        <ng-container [dynamicComponentOutlet]="component" [dynamicComponentOutletOptions]="options"></ng-container>
    `
  })
  class TestComponent {
    component = DynamicComponent;
    options = {label: 'Lotus hydras ducunt ad species.'};
  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        TestComponent,
        DynamicComponent,
        DynamicComponentOutletDirective,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render a component dynamically', () => {
    expect(fixture.debugElement.nativeElement.textContent).toContain('Lotus hydras ducunt ad species.');
  });

  it('should reflect changes to masked options', () => {
    component.options = {label: 'Lotus mortem hic anhelares rumor est.'};

    fixture.detectChanges();

    expect(fixture.debugElement.nativeElement.textContent).toContain('Lotus mortem hic anhelares rumor est.');
  });
});
