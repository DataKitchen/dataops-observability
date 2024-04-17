import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DefaultErrorHandlerComponent } from './default-error-handler.component';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from '@angular/material/snack-bar';

describe('DefaultErrorHandlerComponent', () => {

  let component: DefaultErrorHandlerComponent;
  let fixture: ComponentFixture<DefaultErrorHandlerComponent>;

  let snackbar: MatSnackBarRef<any>;
  let dialog: MatDialog;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DefaultErrorHandlerComponent ],
      providers: [
        MockProvider(MatDialog, class {
          open = jest.fn();
        }),
        MockProvider(MatSnackBarRef, class {
          dismiss = jest.fn();
        }),
        {
          provide: MAT_SNACK_BAR_DATA,
          useValue: {error: new Error('my fantastic error message')}
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DefaultErrorHandlerComponent);
    component = fixture.componentInstance;

    snackbar = TestBed.inject(MatSnackBarRef);
    dialog = TestBed.inject(MatDialog);

    fixture.detectChanges();

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show error message', () => {
    component.onShowMore();
    expect(snackbar.dismiss).toHaveBeenCalled();
    expect(dialog.open).toHaveBeenCalled();
  });

});
