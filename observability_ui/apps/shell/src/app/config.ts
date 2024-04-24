import { Manifest as BaseManifest, RemoteConfig as BaseRemoteConfig } from '@angular-architects/module-federation';

export type RemoteConfig = BaseRemoteConfig & {
  routePath: string;
  remoteName: string;
  exposedModule: string;
  exposedModuleName: string;
};

export type Manifest = BaseManifest<RemoteConfig>;
