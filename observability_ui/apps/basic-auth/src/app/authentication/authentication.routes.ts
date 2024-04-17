import { Route } from '@angular/router';
import { NoAuthGuard } from '@observability-ui/core';
import { AuthenticationComponent } from './authentication.component';
import { LoginComponent } from '../login/login.component';
import { LogoutComponent } from '../logout/logout.component';

export const remoteRoutes: Route[] = [
  {
    path: '',
    component: AuthenticationComponent,
    children: [
      {
        path: 'login',
        component: LoginComponent,
        canActivate: [
          NoAuthGuard,
        ],
      },
      {
        path: 'logout',
        component: LogoutComponent,
        canActivate: [
          NoAuthGuard,
        ],
      },
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'login',
      },
    ],
  }
];
