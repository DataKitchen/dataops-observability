import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ServiceKeyFormComponent } from './service-key-form.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { NgControl } from '@angular/forms';

describe('ServiceKeyFormComponent', () => {
  const ngControl: NgControl = {
    control: {
      clearValidators: jest.fn(),
      addValidators: jest.fn(),
      updateValueAndValidity: jest.fn(),
    }
  } as any;

  let component: ServiceKeyFormComponent;
  let fixture: ComponentFixture<ServiceKeyFormComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [],
      imports: [
        NoopAnimationsModule,
        ServiceKeyFormComponent,
      ],
      providers: []
    }).compileComponents();

    fixture = TestBed.createComponent(ServiceKeyFormComponent);
    component = fixture.componentInstance;

    component['ngControl'] = ngControl;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should add a validator to the form control', () => {
    expect(ngControl.control!.clearValidators).toBeCalled();
    expect(ngControl.control!.addValidators).toBeCalledWith(expect.any(Function));
    expect(ngControl.control!.updateValueAndValidity).toBeCalled();
  });
});
