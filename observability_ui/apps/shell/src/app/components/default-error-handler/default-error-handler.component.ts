import { Component, Inject, TemplateRef, ViewChild } from '@angular/core';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { MAT_LEGACY_SNACK_BAR_DATA as MAT_SNACK_BAR_DATA, MatLegacySnackBarRef as MatSnackBarRef } from '@angular/material/legacy-snack-bar';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'default-error-message',
  template: `
    <div class="message">
      <span>The system encountered an error</span>
      <button mat-button color="warn" (click)="onShowMore()">Show More</button>
    </div>
    <ng-template #dialog>
      <mat-dialog-content>
        {{data.error?.error || message}}
      </mat-dialog-content>
    </ng-template>
  `,
  styles: [ `
    .message {
      display: flex;
      flex-direction: row;
      align-items: baseline;
      justify-content: space-between;
    }

    button {
      padding: 0;
    }
  ` ]
})
export class DefaultErrorHandlerComponent {

  @ViewChild('dialog')
  dialogTpl: TemplateRef<any>;

  constructor(
    private dialog: MatDialog,
    private snackbarRef: MatSnackBarRef<any>,
    @Inject(MAT_SNACK_BAR_DATA) public data: Error,
  ) {
  }

  onShowMore() {
    this.snackbarRef.dismiss();
    this.dialog.open(this.dialogTpl, {data: this.data,});
  }
}
