import { TitleCasePipe } from "@angular/common";
import { Component } from "@angular/core";
import { MatIconModule } from "@angular/material/icon";
import { ComponentType } from "@observability-ui/core";
import { TranslationModule } from "@observability-ui/translate";

@Component({
    selector: 'shell-journey-dag-legend',
    standalone: true,
    imports: [
        TitleCasePipe,
        MatIconModule,
        TranslationModule,
    ],
    template: `
        <div class="legend--item batch">
            <div class="legend--item--icon-wraper">
                <mat-icon svgIcon="batch_pipeline"></mat-icon>
            </div>
            <span>{{ 'componentTypeTag.' + ComponentType.BatchPipeline | translate | titlecase }}</span>
        </div>
        <div class="legend--item dataset">
            <div class="legend--item--icon-wraper">
                <mat-icon svgIcon="dataset"></mat-icon>
            </div>
            <span>{{ 'componentTypeTag.' + ComponentType.Dataset | translate | titlecase }}</span>
        </div>
        <div class="legend--item server">
            <div class="legend--item--icon-wraper">
                <mat-icon svgIcon="server"></mat-icon>
            </div>
            <span>{{ 'componentTypeTag.' + ComponentType.Server | translate | titlecase }}</span>
        </div>
    `,
    styleUrls: [ 'journey-dag-legend.component.scss' ],
})
export class JourneyDagLegendComponent {
    ComponentType = ComponentType;
}
