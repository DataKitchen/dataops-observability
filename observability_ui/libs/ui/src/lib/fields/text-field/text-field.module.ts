import { NgModule } from '@angular/core';
import { TextFieldComponent } from './text-field.component';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { ReactiveFormsModule } from '@angular/forms';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { CommonModule } from '@angular/common';
import { TextFieldErrorComponent } from './text-field-error.component';
import { MatIconModule } from '@angular/material/icon';

@NgModule({
  imports: [
    MatFormFieldModule,
    ReactiveFormsModule,
    MatInputModule,
    CommonModule,
    MatIconModule
  ],
  exports: [
    TextFieldComponent,
    TextFieldErrorComponent,
  ],
  declarations: [
    TextFieldComponent,
    TextFieldErrorComponent,
  ],
  providers: [],
})
export class TextFieldModule {
}
