import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { ElementRefDirective } from './element-ref.directive';

describe('element-ref', () => {

  @Component({
    selector: 'test-component',
    template: `
      <div *ngFor="let item of items" element-ref>{{item}}</div>
    `
  })
  class TestComponent {
    protected readonly items =  ['one', 'two', 'three'];
  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ElementRefDirective],
      declarations: [TestComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });


});
