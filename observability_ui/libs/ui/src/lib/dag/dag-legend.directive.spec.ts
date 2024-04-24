import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, ContentChild } from '@angular/core';
import { DagLegendDirective } from './dag-legend.directive';

describe('dag-legend', () => {

  @Component({
    selector: 'test-component',
    template: `<div dagLegend>...</div>`
  })
  class TestComponent {
    @ContentChild(DagLegendDirective) legend: any;
  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        TestComponent,
        DagLegendDirective,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should be able to query the DOM', () => {
    setTimeout(() => {
        expect(component.legend).toBeInstanceOf(DagLegendDirective);
    }, 1);
  });
});
