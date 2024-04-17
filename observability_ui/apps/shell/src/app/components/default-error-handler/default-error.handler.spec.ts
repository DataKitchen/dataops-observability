import { TestBed } from '@angular/core/testing';
import { DefaultErrorHandler } from './default-error.handler';
import { MatLegacySnackBar as MatSnackBar, MatLegacySnackBarModule as MatSnackBarModule } from '@angular/material/legacy-snack-bar';
import { ErrorHandler } from '@angular/core';
import { MockProvider } from '@datakitchen/ngx-toolkit';

describe('DefaultErrorHandler', () => {

  let service: ErrorHandler;
  let snackbar: MatSnackBar;

  beforeEach(async () => {
    // silence console
    jest.spyOn(console, 'error').mockImplementation();

    await TestBed.configureTestingModule({
      imports: [
        MatSnackBarModule,
      ],
      providers: [
        {provide: ErrorHandler, useClass: DefaultErrorHandler},
        MockProvider(MatSnackBar, class {
          openFromComponent = jest.fn();
        }),
      ],
    });

    service = TestBed.inject(ErrorHandler);
    snackbar = TestBed.inject(MatSnackBar);

  });

  it('should create', () => {
    expect(service).toBeTruthy();
  });

  it('should handle error opening a snackbar', () => {
    service.handleError(new Error('my error'));
    expect(snackbar.openFromComponent).toHaveBeenCalled();
  });

});
