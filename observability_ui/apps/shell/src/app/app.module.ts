import { NgModule } from '@angular/core';
import { BrowserModule, DomSanitizer } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { FlexModule } from '@angular/flex-layout';
import { MatIconModule, MatIconRegistry } from '@angular/material/icon';
import { MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { ServiceWorkerModule } from '@angular/service-worker';
import { BaseHttpInterceptor, CoreModule, EntitiesResolver, FilterParamsInterceptor } from '@observability-ui/core';
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { JWT_OPTIONS } from '@auth0/angular-jwt';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { AppVersionModule } from './app-version/app-version.module';
import { AppRoutingModule } from './app-routing.module';
import { OfflineComponent } from './components/offline/offline.component';
import { environment } from '../environments/environment';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatLegacyListModule as MatListModule } from '@angular/material/legacy-list';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { HeaderComponent } from './components/header/header.component';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { RouterModule } from '@angular/router';
import { TranslationModule } from '@observability-ui/translate';
import { SidenavMenuComponent } from './components/sidenav-menu/sidenav-menu.component';
import { coreTranslations } from './core.translation';
import { MatLegacySnackBarModule as MatSnackBarModule } from '@angular/material/legacy-snack-bar';
import { DefaultErrorHandlerModule } from './components/default-error-handler/default-error-handler.module';
import { EntryComponent } from './components/entry/entry.component';
import { DkTooltipModule, DynamicComponentModule, TruncateModule } from '@observability-ui/ui';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatLegacySlideToggleModule } from '@angular/material/legacy-slide-toggle';
import { NgxMonacoEditorModule } from '@datakitchen/ngx-monaco-editor';

@NgModule({
  declarations: [
    AppComponent,
    OfflineComponent,
    HeaderComponent,
    SidenavMenuComponent,
    EntryComponent,
  ],
  imports: [
    AppRoutingModule,
    BrowserModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatButtonModule,
    FlexModule,
    MatIconModule,
    MatDialogModule,
    ServiceWorkerModule.register('ngsw-worker.js', {
      enabled: environment.production,
      // Register the ServiceWorker as soon as the app is stable
      // or after 30 seconds (whichever comes first).
      registrationStrategy: 'registerWhenStable:30000'
    }),
    CoreModule,
    AppVersionModule,
    HttpClientModule,
    MatSidenavModule,
    MatListModule,
    MatBottomSheetModule,
    MatProgressSpinnerModule,
    MatMenuModule,
    MatLegacySlideToggleModule,
    RouterModule,
    TranslationModule.forRoot(coreTranslations),
    MatSnackBarModule,
    DefaultErrorHandlerModule,
    DynamicComponentModule,
    NgxMonacoEditorModule,
    MatCardModule,
    TruncateModule,
    DkTooltipModule
  ],
  providers: [
    EntitiesResolver,
    {provide: JWT_OPTIONS, useValue: JWT_OPTIONS},
    {provide: HTTP_INTERCEPTORS, useClass: BaseHttpInterceptor, multi: true},
    {provide: HTTP_INTERCEPTORS, useClass: FilterParamsInterceptor, multi: true},
  ],
  bootstrap: [ AppComponent ],
})
export class AppModule {
  constructor(
    domSanitizer: DomSanitizer,
    iconRegistry: MatIconRegistry,
  ) {
    [
      'completed_with_warnings',
      'batch_pipeline',
      'dataset',
      'dbt_core',
      'server',
      'streaming_pipeline',
      'airflow',
      'azure_functions',
      'blob_storage',
      'databricks',
      'data_factory',
      'fivetran',
      'cloud_composer',
      'sqs',
      'talend',
      'power_bi',
      'dataops_testgen',
      'dataops_automation',
      'redshift',
      'snowflake',
      'mssql',
      'postgresql',
      'azure_synapse_pipelines',
      'aws_s3',
      'aws_glue',
      'aws_lambda',
      'aws_sagemaker',
      'azure_ml',
      'tableau',
      'python',
      'informatica',
      'goanywhere',
      'autosys',
      'apache_impala',
      'neo4j',
      'oracle_database',
      'qlik',
    ].forEach(name => iconRegistry.addSvgIcon(name, domSanitizer.bypassSecurityTrustResourceUrl(`/assets/${name}.svg`)));
  }
}
