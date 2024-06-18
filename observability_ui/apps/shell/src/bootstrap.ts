import { InjectionToken, StaticProvider, enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';
import { environment } from './environments/environment';
import { Routes } from '@angular/router';
import { getManifest, loadManifest, loadRemoteModule } from '@angular-architects/module-federation';
import { PLATFORM_ROUTES } from './app/app-routing.module';
import { ComponentReplacement, Manifest, REPLACEMENT_TOKENS } from './app/config';

if (environment.production) {
  enableProdMode();
}

loadManifest('/assets/module-federation.manifest.json').then(async () => {
  const manifest = getManifest<Manifest>();
  const platformRoutes: Routes = [];
  let componentReplacements: Array<ComponentReplacement & {remoteEntry: string}> = [];

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

    componentReplacements = [
      ...componentReplacements,
      ...(entry.replacements?.map(replacement => ({ ...replacement, remoteEntry: entry.remoteEntry})) ?? []),
    ];
  }

  const componentReplacementProviders: StaticProvider[] = [];
  for (const replacement of componentReplacements) {
    const replacementTokens: {[name: string]: InjectionToken<any>} = REPLACEMENT_TOKENS;

    const remoteComponent = await loadRemoteModule({
      type: 'module',
      remoteEntry: replacement.remoteEntry,
      exposedModule: replacement.exposedComponent,
    });

    componentReplacementProviders.push(
      {
        provide: replacementTokens[replacement.token] ?? replacement.token,
        useValue: remoteComponent[replacement.exposedComponentName],
      },
    );
  }

  platformBrowserDynamic([
    {
      provide: PLATFORM_ROUTES,
      useValue: platformRoutes,
    },
    ...componentReplacementProviders,
  ])
    .bootstrapModule(AppModule)
    .catch((err) => console.error(err));
});
