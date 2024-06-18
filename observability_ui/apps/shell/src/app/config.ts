import { Manifest as BaseManifest, RemoteConfig as BaseRemoteConfig } from '@angular-architects/module-federation';
import { ComponentType } from '@angular/cdk/portal';
import { InjectionToken } from '@angular/core';

export type ComponentReplacement = {
  token: string;
  exposedComponent: string;
  exposedComponentName: string;
};

export type RemoteConfig = BaseRemoteConfig & {
  routePath: string;
  remoteName: string;
  exposedModule: string;
  exposedModuleName: string;
  replacements: ComponentReplacement[];
};

export type Manifest = BaseManifest<RemoteConfig>;

export const REPLACEMENT_TOKENS = {
  ProjectsMenu: new InjectionToken<any>('ProjectsMenu'),
  HeaderComponent: new InjectionToken<ComponentType<any> | undefined>('HeaderComponent'),
};
