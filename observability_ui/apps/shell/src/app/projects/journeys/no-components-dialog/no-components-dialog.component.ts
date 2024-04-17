import { Component } from '@angular/core';
import { HelpLinkComponent, EmptyStateSetupComponent } from '@observability-ui/ui';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'shell-no-components-dialog',
  template: `
    <empty-state-setup class="no-components-setup">
      <div class="title">This project has no components</div>
      <div class="body text--secondary">
        Data journeys are built from components and their relationships.<br /><br />
        Integrate your tools so the system can create components when it receives events
      </div>

      <button
        [routerLink]="['..', 'integrations']"
        class="add-button"
        color="primary"
        mat-flat-button>
        <mat-icon class="mr-1">arrow_right_alt</mat-icon>
        Go to Integrations
      </button>

      <help-link class="learn-more"
        href="https://docs.datakitchen.io/article/dataops-observability-help/events-and-components">
        components
      </help-link>
    </empty-state-setup>
  `,
  imports: [
    EmptyStateSetupComponent,
    HelpLinkComponent,
    MatIconModule,
    MatLegacyButtonModule,
    RouterModule
  ],
  styleUrls: [ 'no-components-dialog.component.scss' ],
  standalone: true
})

export class NoComponentsDialogComponent {
  constructor() {
  }
}
