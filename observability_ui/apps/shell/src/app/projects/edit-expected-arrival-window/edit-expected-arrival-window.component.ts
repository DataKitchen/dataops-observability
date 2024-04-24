import { Component, Input } from '@angular/core';
import { Schedule } from '@observability-ui/core';
import { TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { NgFor, NgIf } from '@angular/common';
import { ScheduleFieldModule, TimespanFieldModule } from '@observability-ui/ui';
import { TranslationModule } from '@observability-ui/translate';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'shell-edit-expected-arrival-window',
  templateUrl: 'edit-expected-arrival-window.component.html',
  imports: [
    NgIf,
    ScheduleFieldModule,
    TimespanFieldModule,
    TranslationModule,
    ReactiveFormsModule,
    NgFor
  ],
  standalone: true
})

export class EditExpectedArrivalWindowComponent {
  @Input() form: TypedFormGroup<{
    expectedArrivalWindow: Schedule,
  }>;
}
