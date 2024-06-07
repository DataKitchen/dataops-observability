import { InjectionToken, NgModule } from '@angular/core';
import { RouterModule, ROUTES, Routes } from '@angular/router';
import { IsOnlineGuard } from './guards/is-online.guard';
import { OfflineComponent } from './components/offline/offline.component';
import { AuthGuard, resetStores } from '@observability-ui/core';
import { EntryComponent } from './components/entry/entry.component';
import { ComponentStore } from './projects/components/components.store';
import { InstancesStore } from './stores/instances/instances.store';

export const PLATFORM_ROUTES = new InjectionToken<Routes>('Platform routes for mfe');

const APP_ROUTES: Routes = [
  {
    path: '',
    component: EntryComponent,
    canActivate: [ IsOnlineGuard, AuthGuard ],
  },
  {
    path: 'projects/:projectId',
    canActivate: [
      IsOnlineGuard,
      AuthGuard,
      resetStores(ComponentStore, InstancesStore as any),
    ],
    loadChildren: () => import('./projects/projects.module').then((m) => m.ProjectsModule),
  },
  {
    path: 'offline',
    component: OfflineComponent,
  }
];

@NgModule({
  imports: [
    RouterModule.forRoot(APP_ROUTES, { initialNavigation: 'enabledNonBlocking', enableTracing: false }),
    {
      ngModule: RouterModule,
      providers: [
        {
          provide: ROUTES,
          useFactory: (dynamicRoutes: Routes) => dynamicRoutes,
          deps: [ PLATFORM_ROUTES ],
          multi: true,
        }
      ],
    },
  ],
  exports: [
    RouterModule,
  ],
  declarations: [],
  providers: []
})
export class AppRoutingModule {}
