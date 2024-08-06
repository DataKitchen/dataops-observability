/* eslint-disable @typescript-eslint/ban-ts-comment */
import { APP_INITIALIZER, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SessionService, UserService } from './services';
import { JWT_OPTIONS, JwtHelperService } from '@auth0/angular-jwt';
import { ConfigService } from './config/config.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { tap } from 'rxjs';
import { AppConfiguration } from './config/app-configuration';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CompanyService } from './services/company/company.service';
import { OrganizationService } from './services/organization/organization.service';

import loader from '@monaco-editor/loader';


@NgModule({
  imports: [
    CommonModule,
    HttpClientModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [
    SessionService,
    UserService,
    JwtHelperService,
    ConfigService,
    CompanyService,
    OrganizationService,
    {
      provide: APP_INITIALIZER,
      useFactory: (configService: ConfigService, http: HttpClient) => {
        return () => {
          return http.get<AppConfiguration>(`/environments/environment.json`).pipe(
            tap((config) => {
              configService.setConfig(config);
            }),
          );
        };
      },
      multi: true,
      deps: [ ConfigService, HttpClient ],
    },
    {
      provide: APP_INITIALIZER,
      useFactory: () => {
        return () => {
          return new Promise((resolve) => {
            loader.config({
              paths: {
                vs: '/assets/monaco-editor/min/vs',
              }
            });
            resolve(true);
          });
        };
      },
      multi: true,
    },
    { provide: JWT_OPTIONS, useValue: JWT_OPTIONS }
  ],
  declarations: [],
  exports: []
})
export class CoreModule {
}
