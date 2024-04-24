import { Component, DebugElement } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DkTooltipModule } from './dk-tooltip.module';
import { Overlay } from '@angular/cdk/overlay';
import { By } from '@angular/platform-browser';
import { DkTooltipComponent } from './dk-tooltip.component';
import { ClickListenerService } from './click-listener.service';

// TODO put here because of 👇 check if there's a better way.
// https://stackoverflow.com/questions/39830580/jest-test-fails-typeerror-window-matchmedia-is-not-a-function
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

describe('dkTooltip Directive', () => {
  let fixture: ComponentFixture<DKTooltipTestComponent>;
  let component: DKTooltipTestComponent;

  @Component({
    selector: 'dk-tooltip-demo',
    template: `
      <div>
        <button [dkTooltip]="toolTipTemplate"
                dkTooltipTrigger="click"
                dkTooltipType="dropdown"></button>
        <div [dkTooltip]="toolTipTemplate"
             dkTooltipTrigger="click"
             dkTooltipType="dropdown">
          Test Click on child
          <span id="childElement">I'm the child</span>
        </div>

        <span id="span-with-tooltip"
              dkTooltip="You have to sit, and reject politics by your shining.">
                    Test Hover
                </span>
        <span id="top-tooltip"
              dkTooltip="You have to sit, and reject politics by your shining."
              dkTooltipPlacement="top">
                    Test Hover
                </span>
        <span id="left-tooltip"
              dkTooltip="You have to sit, and reject politics by your shining."
              dkTooltipPlacement="left">
                    Test Hover
                </span>
        <span id="right-tooltip"
              dkTooltip="You have to sit, and reject politics by your shining."
              dkTooltipPlacement="right">
                    Test Hover
                </span>
        <span id="disabled-tooltip"
              dkTooltip="You have to sit, and reject politics by your shining."
              [dkTooltipDisabled]="true">
                    Test Hover
                </span>
      </div>
      <ng-template #toolTipTemplate>
        You have to sit, and reject politics by your shining.
      </ng-template>
    `,
  })
  class DKTooltipTestComponent {
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        DkTooltipModule
      ],
      declarations: [ DKTooltipTestComponent ],
      providers: [
        Overlay,
        ClickListenerService,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(DKTooltipTestComponent);
    component = fixture.componentInstance;
    fixture.autoDetectChanges(true);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('dropdown', () => {
    describe('opening', () => {
      it('should show a tooltip on click', async () => {
        const button = fixture.debugElement.query(By.css('button'));
        button.nativeElement.click();
        await fixture.whenStable();

        const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));
        expect(tooltip).toBeTruthy();
        const overlay = document.getElementsByClassName('cdk-overlay-container');

        expect(overlay[0].textContent).toContain('You have to sit, and reject politics by your shining');
      });

      it('should show a tooltip when clicking on a child element', async () => {
        fixture.debugElement.query(By.css('#childElement')).nativeElement.click();
        await fixture.whenStable();

        const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));
        expect(tooltip).toBeTruthy();
        const overlay = document.getElementsByClassName('cdk-overlay-container');

        expect(overlay[0].textContent).toContain('You have to sit, and reject politics by your shining');
      });
    });

    describe('closing', () => {
      let button: DebugElement;
      let closeButton: DebugElement;
      let overlay: HTMLCollection;

      beforeEach(async () => {
        button = fixture.debugElement.query(By.css('button'));
        button.nativeElement.click();
        await fixture.whenStable();

        const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));

        closeButton = tooltip.query(By.css('button'));
        overlay = document.getElementsByClassName('cdk-overlay-container');

      });

      it('should close when click on X button', async () => {
        closeButton.nativeElement.click();
        await fixture.whenStable();

        expect(overlay[0].textContent).not.toContain('You have to sit, and reject politics by your shining');
      });

      it('should close the tooltip when click again after it is open', () => {

        button.nativeElement.click();

        expect(overlay[0].textContent).not.toContain('You have to sit, and reject politics by your shining');
      });

      it('should close the tooltip when clicking outside', async () => {

        expect(overlay[0].textContent).toContain('You have to sit, and reject politics by your shining');

        fixture.debugElement.nativeElement.click();
        await fixture.whenStable();
        expect(overlay[0].textContent).not.toContain('You have to sit, and reject politics by your shining');

      });

    });
  });

  describe('tooltip', () => {
    let tooltipTriggerEl: DebugElement;

    beforeEach(() => {
      tooltipTriggerEl = fixture.debugElement.query(By.css('#span-with-tooltip'));
    });

    it('should show a tooltip on hover', () => {
      tooltipTriggerEl.triggerEventHandler('mouseenter', null);

      const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));
      expect(tooltip).toBeTruthy();
    });

    it('should hide the tooltip when the mouse leaves the element', () => {
      tooltipTriggerEl.triggerEventHandler('mouseleave', null);

      const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));
      expect(tooltip).toBeFalsy();
    });

    it('should show a tooltip with the specified string', () => {
      tooltipTriggerEl.triggerEventHandler('mouseenter', null);

      const overlay = document.getElementsByClassName('cdk-overlay-container');
      expect(overlay[0].textContent).toContain('You have to sit, and reject politics by your shining');
    });

    it('should set the tooltip placement to bottom by default', () => {
      tooltipTriggerEl.triggerEventHandler('mouseenter', null);

      const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));
      expect(tooltip.componentInstance.placement).toEqual('bottom');
    });

    it('should set the tooltip placement to top', () => {
      tooltipTriggerEl = fixture.debugElement.query(By.css('#top-tooltip'));
      tooltipTriggerEl.triggerEventHandler('mouseenter', null);

      const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));
      expect(tooltip.componentInstance.placement).toEqual('top');
    });

    it('should set the tooltip placement to left', () => {
      tooltipTriggerEl = fixture.debugElement.query(By.css('#left-tooltip'));
      tooltipTriggerEl.triggerEventHandler('mouseenter', null);

      const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));
      expect(tooltip.componentInstance.placement).toEqual('left');
    });

    it('should set the tooltip placement to right', () => {
      tooltipTriggerEl = fixture.debugElement.query(By.css('#right-tooltip'));
      tooltipTriggerEl.triggerEventHandler('mouseenter', null);

      const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));
      expect(tooltip.componentInstance.placement).toEqual('right');
    });

    it('should not open when disabled', () => {
      tooltipTriggerEl = fixture.debugElement.query(By.css('#disabled-tooltip'));
      tooltipTriggerEl.triggerEventHandler('mouseenter', null);

      const tooltip = fixture.debugElement.query(By.directive(DkTooltipComponent));
      expect(tooltip).toBeFalsy();
    });
  });
});
