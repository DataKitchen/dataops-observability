/* eslint-disable @typescript-eslint/ban-ts-comment,no-restricted-syntax */
import 'reflect-metadata';
import { Observable, of, switchMap, tap, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

/**
 * `@Mock()` can be used on any method of any class that extends `ReadOnlyRestApi` which return type is an Observable.
 * It accepts either a variable or a function. If a variable is used its content will be returned as an observable,
 * i.e.: `of(myData)` if a function is given than its arguments should be the same as the decorated method and its
 * return value will be `of`ed.
 *
 * Please note that the call to the endpoint will still be issued so that if the endpoint is available the user will be
 * notified.
 *
 * The mock can be deactivated from the browser setting the sessionStorage such as:
 * sessionStorage.setItem('https://api.base-url/endpoint/company/1/users', true)
 *
 * On the browser's console can be found useful info on the state of the endpoint and the mocked data returned.
 *
 * @example
 *
 * export class ProjectRunsService extends RestApiService<Run> {
 *   [...]
 *
 *   @Mock({
 *     entities: mockRuns,
 *     total: mockRuns.length,
 *   })
 *   override findAll({parentId, ...request}: EntityListRequest<Run> = {}): Observable<EntityListResponse<Run>> {
 *     return super.findAll({parentId, ...request});
 *   }
 *
 *   @Mock((id: string) => {
 *     return mockRuns.find(run => run.id === id);
 *   })
 *   override getOne(id: string, params?: HttpParams): Observable<Run> {
 *     return super.getOne(id, params);
 *   }
 * }
 *
 *
 *
 * @param value
 * @constructor
 */
export function Mock(value?: any) {

  return <T, Fn extends (...args: any[]) => Observable<any>>(target: T, key: string, descriptor: TypedPropertyDescriptor<Fn>) => {


    const originalFunction = descriptor.value;

    // @ts-ignore
    descriptor.value = function (args) {

      const root = this as { getUrl: (parentId: string) => string };

      // @ts-ignore
      const source$ = originalFunction.apply(this, [ args ]);

      const parentId = args && args['parentId'] ? args['parentId'] : '';
      const url = root['getUrl'](parentId);

      const useResponse = JSON.parse(sessionStorage.getItem(url) || 'false');

      return source$.pipe(
        tap(() => {
          console.info(`
  Method "${key}" is mocked but endpoint ["${url}"] is actually returning data
          `);

          if (useResponse) {

            console.info(`
  Returning original data because @Mock is overridden by sessionStorage. You may consider removing @Mock from "${(target as any).constructor.name}.${key}" or run the following in other to use the mocked value anyway:"sessionStorage.removeItem('${url}')"
            `);

          } else {

            console.info(`
  Use "sessionStorage.setItem('${url}', true)" in order to use the original response and/or remove the "@Mock" decorator from "${(target as any).constructor.name}.${key}".
            `);
          }

        }),
        switchMap((resp) => {
          if (useResponse) {
            return of(resp);
          }

          return throwError(() => 'return mocks anyway');

        }),
        catchError(() => {

          let mock = value;

          if (typeof value === 'function') {
            mock = value.apply(this, [ args ]);
          }

          console.info(`
  🧰 skipping call to "${url}". Returning
          `, mock);

          return of(mock);
        }),
      );

    };
  };
}
