import { ENVIRONMENT_INITIALIZER, Injector, NgModule, Optional, inject, reflectComponentType } from '@angular/core';
import { RouterModule } from '@angular/router';
import { SidenavMenuComponent } from '../components/sidenav-menu/sidenav-menu.component';
import { ProjectOverviewComponent } from './overview/overview.component';
import { ProjectsMenu } from './projects.menu.model';
import { DkTooltipModule, DotComponent, DotsChartComponent, DotTemplateDirective, DrillInTemplateDirective, DurationModule, ElementRefDirective, FilterFieldModule, GanttChartModule, HelpLinkComponent, EmptyStateSetupComponent, TableWrapperModule, TextFieldModule, TruncateModule } from '@observability-ui/ui';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { FlexModule } from '@angular/flex-layout';
import { TranslationModule } from '@observability-ui/translate';
import { componentsPanelTranslation } from './component-panel/component-panel.translation';
import { ComponentPanelComponent } from './component-panel/component-panel.component';
import { componentListTranslation } from './components/components-list/component-list.translation';
import { addComponentDialogTranslation } from './components/add-component-dialog/add-component-dialog.translation';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { projectsTranslations } from './projects.translation';
import { ComponentPanelModule } from './component-panel/component-panel.module';
import { EXTRA_TOOL_ICONS, INTEGRATION_TOOLS } from './integrations/integrations.model';
import { AirflowToolComponent } from './integrations/tools/airflow-tool/airflow-tool.component';
import { AWSSQSToolComponent } from './integrations/tools/aws-sqs-tool/aws-sqs-tool.component';
import { AzureBlobStorageToolComponent } from './integrations/tools/azure-blob-storage-tool/azure-blob-storage-tool.component';
import { DatabricksToolComponent } from './integrations/tools/databricks-tool/databricks-tool.component';
import { AzureDataFactoryToolComponent } from './integrations/tools/azure-datafactory-tool/azure-datafactory-tool.component';
import { AzureFunctionsToolComponent } from './integrations/tools/azure-functions-tool/azure-functions-tool.component';
import { FivetranLogConnectorToolComponent } from './integrations/tools/fivetran-logs-tool/fivetran-logs-tool.component';
import { GoogleCloudComposerToolComponent } from './integrations/tools/cloud-composer-tool/cloud-composer-tool.component';
import { PowerBIToolComponent } from './integrations/tools/power-bi-tool/power-bi-tool.component';
import { TalendToolComponent } from './integrations/tools/talend-tool/talend-tool.component';
import { DBTCoreToolComponent } from './integrations/tools/dbt-core-tool/dbt-core-tool.component';
import { AzureSynapsePipelinesToolComponent } from './integrations/tools/azure-synapse-pipelines-tool/azure-synapse-pipelines-tool.component';
import { CdkConnectedOverlay, CdkOverlayOrigin } from '@angular/cdk/overlay';
import { MatLegacyProgressBarModule } from '@angular/material/legacy-progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatLegacyProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { MultipleComponentPanelComponent } from './multiple-component-panel/multiple-component-panel.component';
import { ProjectDisplayComponent } from './project-display/project-display.component';
import { SSISToolComponent } from './integrations/tools/ssis-tool/ssis-tool.component';
import { QlikToolComponent } from './integrations/tools/qlik-tool/qlik-tool.component';
import { REPLACEMENT_TOKENS } from '../../app/config';
import { Menu } from '../components/sidenav-menu/sidenav-menu.model';
import { RULE_ACTIONS } from "../components/rules-actions/actions.model";
import { SendEmailActionComponent } from "../components/rules-actions/implementations/actions/send-email/send-email-action.component";
import { WebhookActionComponent } from "../components/rules-actions/implementations/actions/webhook/webhook-action.component";

let injector!: Injector; // https://github.com/angular/angular/issues/51532

@NgModule({
  declarations: [
    ProjectOverviewComponent,
    ProjectDisplayComponent,
  ],
  imports: [
    ReactiveFormsModule,
    RouterModule.forChild([
      {
        path: 'overview',
        component: ProjectOverviewComponent,
        data: {
          helpLink: 'article/dataops-observability-help/project-overview'
        }
      },
      {
        path: 'components',
        loadChildren: () => import('./components/components.module').then((m) => m.ComponentsModule)
      },
      {
        path: 'events',
        loadChildren: () => import('./events/events.module').then((m) => m.EventsModule)
      },
      {
        path: 'runs',
        loadChildren: () => import('./runs/runs.module').then((m) => m.RunsModule)
      },
      {
        path: 'journeys',
        loadChildren: () => import('./journeys/journeys.module').then((m) => m.JourneysModule)
      },
      {
        path: 'instances',
        loadChildren: () => import('./instances/instances.module').then((m) => m.InstancesModule)
      },
      {
        path: 'integrations',
        loadChildren: () => import('./integrations/integrations.module').then((m) => m.IntegrationsModule)
      },
      {
        path: 'api-keys',
        loadComponent: () => import('./api-keys/api-keys.component').then((c) => c.APIKeysComponent),
        data: {
          helpLink: 'article/dataops-observability-help/api-keys'
        }
      },
      {
        path: 'settings',
        loadComponent: () => import('./settings/settings.component').then((c) => {
          // https://github.com/angular/angular/issues/28136
          const componentMetadata = reflectComponentType(c.SettingsComponent);
          return injector.get(componentMetadata.selector, c.SettingsComponent);
        }),
        data: {
          helpLink: 'article/dataops-observability-help/project-settings'
        }
      },
      {

        path: '',
        pathMatch: 'full',
        redirectTo: 'overview'
      },
      {
        path: '',
        component: SidenavMenuComponent,
        resolve: {
          menus: 'menusResolver'
        },
        outlet: 'sidenav'
      },
      {
        path: ':id',
        outlet: 'rightPanel',
        component: ComponentPanelComponent
      },
      {
        path: 'multiple/:ids',
        outlet: 'rightPanel',
        component: MultipleComponentPanelComponent
      }
    ]),
    GanttChartModule,
    CommonModule,
    TextFieldModule,
    FlexModule,
    TranslationModule.forChild({
      ...projectsTranslations,
      ...componentsPanelTranslation,
      ...componentListTranslation,
      ...addComponentDialogTranslation
    }),
    TableWrapperModule,
    DkTooltipModule,
    TruncateModule,
    DurationModule,
    MatIconModule,
    MatButtonModule,
    ComponentPanelModule,
    FilterFieldModule,
    CdkOverlayOrigin,
    CdkConnectedOverlay,
    MatLegacyProgressBarModule,
    ElementRefDirective,
    MatDividerModule,
    DotComponent,
    DotTemplateDirective,
    DotsChartComponent,
    DrillInTemplateDirective,
    MatLegacyProgressSpinnerModule,
    EmptyStateSetupComponent,
    HelpLinkComponent
  ],
  providers: [
    {
      provide: ENVIRONMENT_INITIALIZER,
      useFactory: () => {
        injector = inject(Injector);
        return () => {};
      },
      multi: true,
    },
    {
      provide: 'menusResolver',
      useFactory: (replacementMenu: Menu[]) => {
        return () => {
          return replacementMenu ?? ProjectsMenu;
        };
      },
      deps: [[new Optional(), REPLACEMENT_TOKENS.ProjectsMenu]]
    },
    {
      provide: INTEGRATION_TOOLS,
      useValue: [
        AirflowToolComponent,
        AWSSQSToolComponent,
        AzureBlobStorageToolComponent,
        AzureDataFactoryToolComponent,
        AzureFunctionsToolComponent,
        AzureSynapsePipelinesToolComponent,
        DatabricksToolComponent,
        DBTCoreToolComponent,
        FivetranLogConnectorToolComponent,
        GoogleCloudComposerToolComponent,
        PowerBIToolComponent,
        SSISToolComponent,
        QlikToolComponent,
        TalendToolComponent,
      ],
    },
    {
      provide: EXTRA_TOOL_ICONS,
      useValue: [
        { _name: 'redshift', _displayName: 'Amazon Redshift', _icon: 'redshift' },
        { _name: 'snowflake', _displayName: 'Snowflake', _icon: 'snowflake' },
        { _name: 'mssql', _displayName: 'Microsoft SQL Server', _icon: 'mssql' },
        { _name: 'postgresql', _displayName: 'PostgreSQL', _icon: 'postgresql' },
        { _name: 'aws_glue', _displayName: 'AWS Glue', _icon: 'aws_glue' },
        { _name: 'aws_lambda', _displayName: 'AWS Lambda', _icon: 'aws_lambda' },
        { _name: 'aws_sagemaker', _displayName: 'Amazon Sagemaker', _icon: 'aws_sagemaker' },
        { _name: 'azure_ml', _displayName: 'Azure ML', _icon: 'azure_ml' },
        { _name: 'tableau', _displayName: 'Tableau', _icon: 'tableau' },
        { _name: 'python', _displayName: 'Python', _icon: 'python' },
        { _name: 'dataops_automation', _displayName: 'DataKitchen DataOps Automation', _icon: 'dataops_automation' },
        { _name: 'informatica', _displayName: 'Informatica', _icon: 'informatica' },
        { _name: 'goanywhere', _displayName: 'GoAnywhere', _icon: 'goanywhere' },
        { _name: 'autosys', _displayName: 'AutoSys', _icon: 'autosys' },
        { _name: 'apache_impala', _displayName: 'Apache Impala', _icon: 'apache_impala' },
        { _name: 'neo4j', _displayName: 'Neo4j', _icon: 'neo4j' },
        { _name: 'oracle_database', _displayName: 'Oracle Database', _icon: 'oracle_database' },
      ],
    },
    {
      provide: RULE_ACTIONS,
      useValue: [
        SendEmailActionComponent,
        WebhookActionComponent,
        // ExampleActionComponent,
      ],
    },

  ],
  exports: []
})
export class ProjectsModule {
}
