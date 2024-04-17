import { Component, Input } from '@angular/core';
import { AsyncPipe, NgIf } from '@angular/common';
import { DkTooltipModule, ScheduleFieldModule, TimespanFieldModule } from '@observability-ui/ui';
import { MatIconModule } from '@angular/material/icon';
import { TranslationModule } from '@observability-ui/translate';
import { ReactiveFormsModule } from '@angular/forms';
import { Schedule } from '@observability-ui/core';
import { TypedFormGroup } from '@datakitchen/ngx-toolkit';

@Component({
  selector: 'shell-edit-expected-schedule',
  templateUrl: 'edit-expected-schedule.component.html',
  imports: [
    AsyncPipe,
    DkTooltipModule,
    MatIconModule,
    NgIf,
    ScheduleFieldModule,
    TimespanFieldModule,
    TranslationModule,
    ReactiveFormsModule
  ],
  standalone: true
})

export class EditExpectedScheduleComponent {
  @Input() form: TypedFormGroup<{
    startsAt: Schedule,
    endsAt: Schedule,
  }>;
}
