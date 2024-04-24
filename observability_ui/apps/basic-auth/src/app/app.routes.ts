import { Route } from '@angular/router';

export const appRoutes: Route[] = [
  {path: '', loadChildren: () => import('./authentication/authentication.module').then(m => m.AuthenticationModule)},
];
