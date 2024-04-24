import { TestBed } from '@angular/core/testing';
import { Directive } from '@angular/core';
import { Subject } from 'rxjs';
import { Params } from '@angular/router';
import { BindQueryParamsAbstract } from './bind-query-params.abstract';
import { Mocked, MockService } from '@datakitchen/ngx-toolkit';
import { ParameterService } from '@datakitchen/ngx-toolkit';

describe('bind-query-params.abstract', () => {

  @Directive({
    selector: '[testBindQueryParams]',
  })
    // eslint-disable-next-line @angular-eslint/directive-class-suffix
  class BindQueryParamsImpl extends BindQueryParamsAbstract {

    setInitialSpy = jest.fn();

    override source$!: Subject<Params>;

    constructor(
      protected paramService: ParameterService,
    ) {
      super(paramService, new Subject());
    }

    protected setInitialValue(params: Params) {
      this.setInitialSpy(params);
    }
  }

  let instance: BindQueryParamsImpl;
  let parameterService: Mocked<ParameterService>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        BindQueryParamsImpl,
        {provide: ParameterService, useClass: MockService(ParameterService)()},
      ],

    }).compileComponents();

    instance = TestBed.inject(BindQueryParamsImpl);
    parameterService = TestBed.inject(ParameterService) as Mocked<ParameterService>;
  });

  it('should create', () => {
    expect(instance).toBeTruthy();
  });

  describe('AfterViewInit', () => {
    const params = {
      x: 'gojira',
      y: 'mothra',
    };

    it('should parse and set initial values from query params', () => {
      parameterService.getQueryParams.mockReturnValue(params);
      instance.ngAfterViewInit();

      expect(instance.setInitialSpy).toHaveBeenCalledWith(params);
    });

    it('should parse and set new values as query params, when source emits', () => {
      instance.ngAfterViewInit();
      const values = {
        a: 'ghidorah',
        b: 'rodan',
      };
      instance.source$.next(values);

      expect(parameterService.setQueryParams).toHaveBeenCalledWith(values);
    });

    describe('when waiting for parent component', () => {
      beforeEach(() => {
        parameterService.getQueryParams.mockReturnValue(params);
        instance.waitForParent = true;
      });

      it('should not set the initial value right away', () => {
        instance.ngAfterViewInit();
        expect(instance.setInitialSpy).not.toBeCalled();
      });

      it('should set the initial value after the parentInitialized input is set to true', () => {
        instance.ngAfterViewInit();
        instance.parentInitialized = true;
        expect(instance.setInitialSpy).toBeCalledWith(params);
      });

      it('should set the initial value only once', () => {
        instance.ngAfterViewInit();
        instance.parentInitialized = true;
        instance.parentInitialized = false;
        instance.parentInitialized = true;

        expect(instance.setInitialSpy).toBeCalledTimes(1);
      });
    });
  });
});
