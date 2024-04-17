import { Component, ViewChild } from '@angular/core';
import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { MatLegacyPaginator as MatPaginator, MatLegacyPaginatorModule as MatPaginatorModule, LegacyPageEvent as PageEvent } from '@angular/material/legacy-paginator';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { Mocked, MockService } from '@datakitchen/ngx-toolkit';
import { ParameterService, StorageService } from '@datakitchen/ngx-toolkit';
import { BindQueryParamsMatPaginatorDirective } from './bind-query-params-mat-paginator.directive';

describe('bind-query-params-mat-paginator', () => {

  @Component({
    selector: 'test-component',
    template: `
      <mat-paginator #paginator
                     [length]="items.length"
                     [pageIndex]="pageIndex"
                     [pageSize]="pageSize"
                     [pageSizeOptions]="pageSizeOptions"
                     (page)="onPageChange($event)"
                     bindQueryParamsMatPaginator
                     queryParamsNamespace="namespace"
                     [sizeStorageKey]="storageKey">

      </mat-paginator>
    `,
  })
  class TestComponent {
    @ViewChild('paginator')
    paginator: MatPaginator;

    items = new Array(100);
    pageIndex = 0;
    pageSize = 10;
    pageSizeOptions = [ 1, 10, 20 ];
    storageKey = 'sizeKey';

    onPageChange = jest.fn<any, [PageEvent]>();
  }

  let fixture: ComponentFixture<TestComponent>;
  let comp: TestComponent;
  let parameterService: Mocked<ParameterService>;
  let storageService: Mocked<StorageService>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatPaginatorModule,
        NoopAnimationsModule,
      ],
      declarations: [
        TestComponent,
        BindQueryParamsMatPaginatorDirective,
      ],
      providers: [
        {provide: ParameterService, useClass: MockService(ParameterService)()},
        {provide: StorageService, useClass: MockService(StorageService)()},
      ],
    }).compileComponents();

    parameterService = TestBed.inject(ParameterService) as Mocked<ParameterService>;
    parameterService.getQueryParams.mockReturnValue({namespace_pageIndex: '2', namespace_pageSize: '20'});

    storageService = TestBed.inject(StorageService) as Mocked<StorageService>;
    storageService.getStorage.mockReturnValue(100);

    fixture = TestBed.createComponent(TestComponent);
    comp = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(comp).toBeTruthy();
  });

  it('should set initial values from queryParams', fakeAsync(() => {
    tick();
    expect(comp.paginator.pageIndex).toEqual(2);
    expect(comp.paginator.pageSize).toEqual(20);
    expect(comp.onPageChange).toHaveBeenCalledWith({pageIndex: 2, pageSize: 20});
  }));

  it('should set initial page size from local storage, if no queryParams', fakeAsync(() => {
    parameterService.getQueryParams.mockReturnValue({});
    fixture = TestBed.createComponent(TestComponent);
    comp = fixture.componentInstance;
    fixture.detectChanges();
    tick();

    expect(comp.paginator.pageIndex).toEqual(0);
    expect(comp.paginator.pageSize).toEqual(100);
  }));

  it('should set query params when page changes', () => {
    comp.paginator.nextPage();
    expect(parameterService.setQueryParams).toHaveBeenCalledWith({namespace_pageIndex: 3, namespace_pageSize: 20});
  });

  it('should set query params when page changes size', () => {
    comp.paginator._changePageSize(10);
    expect(parameterService.setQueryParams).toHaveBeenCalledWith({namespace_pageIndex: 4, namespace_pageSize: 10});
  });

  it('should set local storage when page changes size', () => {
    comp.paginator._changePageSize(10);
    expect(storageService.setStorage).toHaveBeenCalledWith(comp.storageKey, 10);
  });

  it('should set query params when page changes programmatically', () => {
    comp.pageIndex = 5;
    comp.pageSize = 50;
    fixture.detectChanges();

    expect(parameterService.setQueryParams).toHaveBeenCalledWith({namespace_pageIndex: 5, namespace_pageSize: 50});
  });
});
