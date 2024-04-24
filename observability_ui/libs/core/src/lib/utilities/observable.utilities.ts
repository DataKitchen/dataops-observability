import { defer, from, iif, max as rxjsMax, min as rxjsMin, MonoTypeOperatorFunction, Observable, of, switchMap } from 'rxjs';

export function min<T>(comparer?: (x: T, y: T) => number, startValueFn?: () => T): (source: Observable<Array<T>>) => Observable<T> {
  return comparisonOperator(rxjsMin(comparer), startValueFn);
}

export function max<T>(comparer?: (x: T, y: T) => number, startValueFn?: () => T): (source: Observable<Array<T>>) => Observable<T> {
  return comparisonOperator(rxjsMax(comparer), startValueFn);
}

function comparisonOperator<T>(
  operator: MonoTypeOperatorFunction<T>,
  startValueFn?: () => T
): (source: Observable<Array<T>>) => Observable<T> {
  return (source: Observable<Array<T>>): Observable<T> => {
    return source.pipe(
      switchMap((items: Array<T>) =>
        iif(
          () => items.length > 0,
          from(items).pipe(
            operator,
          ),
          defer(() => of(startValueFn?.()))
        )
      ),
    ) as Observable<T>;
  };
}
