import { AfterViewInit, Directive, Input, OnDestroy } from '@angular/core';
import { Params } from '@angular/router';
import { filter, map, take, takeUntil, tap } from 'rxjs/operators';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { ParameterService } from '@datakitchen/ngx-toolkit';

@Directive()
export abstract class BindQueryParamsAbstract implements AfterViewInit, OnDestroy {

  @Input() waitForParent: boolean = false;

  @Input() set parentInitialized(value: boolean) {
    this.parentComponentInitialized$.next(value);
  }

  private parentComponentInitialized$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);

  private destroyed$ = new Subject<void>();

  constructor(
    protected parameterService: ParameterService,
    protected source$?: Observable<any>,
  ) {}

  ngAfterViewInit(): void {
    // subscribe here to make sure that async pipes have been processed already
    const params = this.parameterService.getQueryParams();
    const initialValue = this.parseInitialValue(params);

    this.parentComponentInitialized$.pipe(
      filter(initialized => this.waitForParent ? initialized : true),
      take(1),
      tap(() => this.setInitialValue(initialValue)),
      takeUntil(this.destroyed$),
    ).subscribe();

    this.source$?.pipe(
      map((values) => this.parseValuesToParams(values)),
      tap((values) => this.parameterService.setQueryParams(values)),
      takeUntil(this.destroyed$),
    ).subscribe();
  }

  /**
   * Parses query parameters and set them on the bound component
   * i.e.:
   * - in case of a FormGroup we would need to call formGroup.patchValue
   * - in case of a MatPaginator we want to call this.paginator.page.next
   *
   * @param params query parameters as they're seen when loading the page
   * @protected
   */
  protected abstract setInitialValue(params: unknown): void;

  /**
   * Parses query parameters so that they can be used to be nexted on `source$`
   *
   * @param params
   * @protected
   * @returns the parsed query params
   */
  protected parseInitialValue(params: Params): Params {
    return params;
  }

  parseValuesToParams(values: Params): Params {
    return values;
  }

  ngOnDestroy() {
    this.destroyed$.next();
    this.destroyed$.complete();
  }
}
