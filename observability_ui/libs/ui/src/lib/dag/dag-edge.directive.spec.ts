import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { DagEdgeDirective } from './dag-edge.directive';

describe('dag-edge', () => {

  @Component({
    selector: 'test-component',
    template: `<dag-edge></dag-edge>`
  })
  class TestComponent {
  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        TestComponent,
        DagEdgeDirective,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
