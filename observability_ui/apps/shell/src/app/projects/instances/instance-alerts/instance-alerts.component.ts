import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { aggregateAlerts } from '@observability-ui/core';
import { Instance } from '@observability-ui/core';
import { DkTooltipModule } from '@observability-ui/ui';
import { NgFor, NgIf } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { TranslationModule } from '@observability-ui/translate';

@Component({
  selector: 'shell-instance-alerts',
  templateUrl: './instance-alerts.component.html',
  standalone: true,
  styleUrls: [ './instance-alerts.component.scss' ],
  imports: [
    DkTooltipModule,
    NgIf,
    MatIconModule,
    TranslationModule,
    NgFor
  ]
})
export class InstanceAlertsComponent implements OnChanges {
  @Input() instance: Instance;

  @Output() alertClicked = new EventEmitter<void>();

  errorAlerts: { count: number; descriptions: string[] } = { count: 0, descriptions: [] };
  warningAlerts: { count: number; descriptions: string[] } = { count: 0, descriptions: [] };

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['instance']) {
      const { errors, warnings } = aggregateAlerts(this.instance.alerts_summary);

      this.errorAlerts.count = errors.count;
      this.errorAlerts.descriptions = errors.alerts.map(a => a.description);

      this.warningAlerts.count = warnings.count;
      this.warningAlerts.descriptions = warnings.alerts.map(a => a.description);
    }
  }
}
