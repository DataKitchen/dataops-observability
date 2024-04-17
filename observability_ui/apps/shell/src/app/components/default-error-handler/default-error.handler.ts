import { ErrorHandler, Injectable } from '@angular/core';
import { MatLegacySnackBar as MatSnackBar } from '@angular/material/legacy-snack-bar';
import { DefaultErrorHandlerComponent } from './default-error-handler.component';


@Injectable({
  providedIn: 'root'
})
export class DefaultErrorHandler extends ErrorHandler {

  constructor(
    private snackbar: MatSnackBar,
  ) {
    super();
  }

  override handleError(error: any) {
    super.handleError(error);
    this.snackbar.openFromComponent(DefaultErrorHandlerComponent, {duration: 3000, data: error, });
  }

}
