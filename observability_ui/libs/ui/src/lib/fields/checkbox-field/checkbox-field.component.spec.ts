import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CheckboxFieldComponent } from './checkbox-field.component';
import { MockComponent } from 'ng-mocks';
import { MatCheckbox } from '@angular/material/checkbox';

describe('checkbox-field', () => {

  let component: CheckboxFieldComponent;
  let fixture: ComponentFixture<CheckboxFieldComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        CheckboxFieldComponent,
        MockComponent(MatCheckbox),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CheckboxFieldComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
