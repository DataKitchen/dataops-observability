import { ErrorHandler, NgModule } from '@angular/core';
import { DefaultErrorHandler } from './default-error.handler';
import { MatLegacySnackBarModule as MatSnackBarModule } from '@angular/material/legacy-snack-bar';
import { MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { DefaultErrorHandlerComponent } from './default-error-handler.component';

@NgModule({
  imports: [
    MatDialogModule,
    MatSnackBarModule,
    MatButtonModule,
  ],
  exports: [
    DefaultErrorHandlerComponent,
  ],
  declarations: [
    DefaultErrorHandlerComponent,
  ],
  providers: [
    {provide: ErrorHandler, useClass: DefaultErrorHandler},
  ],
})
export class  DefaultErrorHandlerModule {
}
