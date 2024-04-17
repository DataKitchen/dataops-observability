import { By } from '@angular/platform-browser';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DkTooltipComponent } from './dk-tooltip.component';
import { MockComponent } from 'ng-mocks';
import { MatIcon } from '@angular/material/icon';

describe('dk-tooltip Component', () => {
  let component: DkTooltipComponent;
  let fixture: ComponentFixture<DkTooltipComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        DkTooltipComponent,
        MockComponent(MatIcon),
      ],
    });

    fixture = TestBed.createComponent(DkTooltipComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('dropdown', () => {
    beforeEach(async () => {
      component.type = 'dropdown';
      fixture.detectChanges();
      await fixture.whenStable();
    });

    it('should have the dropdown flag true', () => {
      expect(component.isDropdown).toBeTruthy();
    });

    it('should have a .dk-dropdown css classname', () => {
      const container = fixture.debugElement.query(By.css('.dk-dropdown'));
      expect(container).toBeTruthy();
    });

    it('should next true in the close subject when closing', done => {
      component.close$.subscribe({
        next: closed => {
          expect(closed).toBeTruthy();
          done();
        },
      });

      component.close();
    });

    it('should have a close icon button', done => {
      component.close$.subscribe({
        next: closed => {
          expect(closed).toBeTruthy();
          done();
        },
      });

      const iconButton = fixture.debugElement.query(By.css('[mat-icon-button]'));
      iconButton.nativeElement.click();
    });
  });

  describe('tooltip', () => {
    beforeEach(async () => {
      component.type = 'tooltip';
      fixture.detectChanges();
      await fixture.whenStable();
    });

    it('should have the dropdown flag false', () => {
      expect(component.isDropdown).toBeFalsy();
    });

    it('should have a .dk-tooltip css classname', () => {
      const container = fixture.debugElement.query(By.css('.dk-tooltip'));
      expect(container).toBeTruthy();
    });

    it('should have a .dk-tooltip-top with placement=top', async () => {
      component.placement = 'top';
      fixture.detectChanges();
      await fixture.whenStable();

      const container = fixture.debugElement.query(By.css('.dk-tooltip-top'));
      expect(container).toBeTruthy();
    });

    it('should have a .dk-tooltip-bottom with placement=bottom', async () => {
      component.placement = 'bottom';
      fixture.detectChanges();
      await fixture.whenStable();

      const container = fixture.debugElement.query(By.css('.dk-tooltip-bottom'));
      expect(container).toBeTruthy();
    });

    it('should have a .dk-tooltip-left with placement=left', async () => {
      component.placement = 'left';
      fixture.detectChanges();
      await fixture.whenStable();

      const container = fixture.debugElement.query(By.css('.dk-tooltip-left'));
      expect(container).toBeTruthy();
    });

    it('should have a .dk-tooltip-right with placement=right', async () => {
      component.placement = 'right';
      fixture.detectChanges();
      await fixture.whenStable();

      const container = fixture.debugElement.query(By.css('.dk-tooltip-right'));
      expect(container).toBeTruthy();
    });
  });
});
