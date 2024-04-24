/* istanbul ignore file */
import { ConfigService } from './config.service';
import { filter, map, take } from 'rxjs';
import { AppConfiguration } from './app-configuration';

export function ProvideFromConfig(provide: any, key: keyof AppConfiguration, mapFn: (value: any) => any = (v) => v) {
  return {
    provide: provide,
    useFactory: (config: ConfigService) => {
      return config.ready$.pipe(
        filter((ready) => ready),
        map(() => {
          return config.get(key);
        }),
        map((value) => mapFn(value)),
        take(1),
      );

    },
    deps: [ ConfigService ]
  };
}
