import { Component, ViewChild } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { MatLegacyTabsModule as MatTabsModule, MatLegacyTabGroup as MatTabGroup } from '@angular/material/legacy-tabs';
import { Mocked, MockService } from '@datakitchen/ngx-toolkit';
import { ParameterService } from '@datakitchen/ngx-toolkit';
import { BindQueryParamsMatTabDirective } from './bind-query-params-mat-tab.directive';

describe('bind-query-params-mat-tab', () => {

  const tabNames = [ 'Tab1', 'Tab2' ];

  @Component({
    selector: 'test-component',
    template: `
      <mat-tab-group #tabGroup
                     bindQueryParamsMatTab="tab"
                     [tabNames]="useTabNames ? tabNames : null">
        <mat-tab label="one">
          my first tab
        </mat-tab>
        <mat-tab label="two">
          my second tab
        </mat-tab>
      </mat-tab-group>
    `,
  })
  class TestComponent {
    @ViewChild('tabGroup')
    tabGroup!: MatTabGroup;

    tabNames = tabNames;
    useTabNames = false;
  }

  let fixture: ComponentFixture<TestComponent>;
  let comp: TestComponent;
  let parameterService: Mocked<ParameterService>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatTabsModule,
        NoopAnimationsModule,
      ],
      declarations: [
        TestComponent,
        BindQueryParamsMatTabDirective,
      ],
      providers: [
        {provide: ParameterService, useClass: MockService(ParameterService)()},
      ],
    }).compileComponents();

    parameterService = TestBed.inject(ParameterService) as Mocked<ParameterService>;
    parameterService.getQueryParams.mockReturnValue({});

    fixture = TestBed.createComponent(TestComponent);
    comp = fixture.componentInstance;
  });

  it('should create', () => {
    expect(comp).toBeTruthy();
  });

  describe('setInitialValue()', () => {

    it('should set initial values: tab indexes', async () => {
      parameterService.getQueryParams.mockReturnValue({tab: 1});
      fixture.detectChanges(); // Trigger ngAfterViewInit
      fixture.detectChanges(); // Trigger updated to tabGroup.selectedIndex
      await fixture.whenStable();
      expect(comp.tabGroup.selectedIndex).toEqual(1);
    });

    it('should set initial values: tab names', async () => {
      parameterService.getQueryParams.mockReturnValue({tab: tabNames[1]});
      comp.useTabNames = true;
      fixture.detectChanges(); // Trigger ngAfterViewInit
      fixture.detectChanges(); // Trigger updated to tabGroup.selectedIndex
      await fixture.whenStable();
      expect(comp.tabGroup.selectedIndex).toEqual(1);
    });
  });

  describe('parseValuesToParams()', () => {

    it('should update queryParam on tab change: tab indexes', async () => {
      fixture.detectChanges();
      comp.tabGroup.selectedIndexChange.next(1);
      fixture.detectChanges();
      await fixture.whenStable();
      expect(parameterService.setQueryParams).toHaveBeenCalledWith({tab: 1});
    });

    it('should update queryParam on tab change: tab names', async () => {
      comp.useTabNames = true;
      fixture.detectChanges();
      comp.tabGroup.selectedIndexChange.next(1);
      fixture.detectChanges();
      await fixture.whenStable();
      expect(parameterService.setQueryParams).toHaveBeenCalledWith({tab: tabNames[1]});
    });
  });
});
