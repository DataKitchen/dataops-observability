import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TextFieldErrorComponent } from './text-field-error.component';

describe('text-field-error', () => {

  let component: TextFieldErrorComponent;
  let fixture: ComponentFixture<TextFieldErrorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TextFieldErrorComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(TextFieldErrorComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
