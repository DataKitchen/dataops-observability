import { ChangeDetectionStrategy, Component, computed, Inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { AbstractTool } from './abstract-tool.directive';
import { INTEGRATION_TOOLS } from '../integrations.model';
import { ProjectService } from '@observability-ui/core';
import { ActivatedRoute } from '@angular/router';
import { map } from 'rxjs';

@Component({
  selector: 'shell-tool-display',
  template: `
    <div class="backdrop"
      [routerLink]="['.']"
      [relativeTo]="integrationsRoute"></div>

    <div class="top">
      <a routerLink=".."
        class="back-link">
        <mat-icon>arrow_back</mat-icon>
        Back to Integrations
      </a>

      <a routerLink="."
        [relativeTo]="integrationsRoute"
        class="close-button"
        mat-icon-button>
        <mat-icon>close</mat-icon>
      </a>
    </div>

    <ng-container *ngIf="toolName()">
      <ng-container
        [dynamicComponentOutlet]="toolComponent()"
        [dynamicComponentOutletOptions]="{}">
      </ng-container>
    </ng-container>
  `,
  styleUrls: [ 'tool-display.component.scss' ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolDisplayComponent {
  integrationsRoute = this.route.parent!.parent;

  toolName = toSignal(
    this.route.params.pipe(
      map(({ tool }) => tool),
    )
  );
  toolComponent = computed(() => this.tools.find((tool) => tool._name === this.toolName()));

  constructor(
    private route: ActivatedRoute,
    private service: ProjectService,
    @Inject(INTEGRATION_TOOLS) private tools: typeof AbstractTool[],
  ) {}
}
