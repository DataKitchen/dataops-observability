import { NgModule } from '@angular/core';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { ReactiveFormsModule } from '@angular/forms';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { ScheduleFieldComponent } from './schedule-field.component';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { OverlayModule } from '@angular/cdk/overlay';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { PortalModule } from '@angular/cdk/portal';
import { MatLegacyCheckboxModule as MatCheckboxModule } from '@angular/material/legacy-checkbox';
import { SchedulePipe } from './schedule.pipe';
import { HelpLinkComponent } from '../../help-link/help-link.component';

@NgModule({
  imports: [
    CommonModule,
    ReactiveFormsModule,

    MatButtonModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatSelectModule,
    OverlayModule,
    PortalModule,
    HelpLinkComponent
  ],
  exports: [
    ScheduleFieldComponent,
    SchedulePipe,
  ],
  declarations: [
    ScheduleFieldComponent,
    SchedulePipe,
  ],
  providers: [],
})
export class ScheduleFieldModule {
}
