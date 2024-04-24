import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Component } from '@angular/core';
import { TextFieldModule } from './text-field.module';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('text-field', () => {

  @Component({
    selector: 'test-component',
    template: `
      <text-field label="my label" hint="my hint" [formControl]="form"></text-field>
    `
  })
  class TestComponent {
    form = new FormControl();
  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        TestComponent,
      ],
      imports: [
        ReactiveFormsModule,
        NoopAnimationsModule,
        TextFieldModule,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
