import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';
import { environment } from './environments/environment';
import { Routes } from '@angular/router';
import { getManifest, loadManifest, loadRemoteModule } from '@angular-architects/module-federation';
import { PLATFORM_ROUTES } from './app/app-routing.module';
import { Manifest } from './app/config';

if (environment.production) {
  enableProdMode();
}

loadManifest('/assets/module-federation.manifest.json').then(async () => {
  const manifest = getManifest<Manifest>();
  const platformRoutes: Routes = [];

  for (const key of Object.keys(manifest)) {
    const entry = manifest[key];

    platformRoutes.push({
      path: entry.routePath,
      loadChildren: () =>
        loadRemoteModule({
          type: 'manifest',
          remoteName: entry.remoteName,
          exposedModule: entry.exposedModule,
        }).then((m) => m[entry.exposedModuleName])
    });
  }

  platformBrowserDynamic([
    {
      provide: PLATFORM_ROUTES,
      useValue: platformRoutes,
    },
  ])
    .bootstrapModule(AppModule)
    .catch((err) => console.error(err));
});
