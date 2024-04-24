import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HelpLinkComponent } from './help-link.component';

const originalLocation = window;

describe('HelpLinkComponent', () => {
  const popup: Window = {location: {href: ''}, closed: false} as any;

  let component: HelpLinkComponent;
  let fixture: ComponentFixture<HelpLinkComponent>;

  let windowOpenPopup: jest.Mock;
  let preventDefault: jest.Mock;
  let stopImmediatePropagation: jest.Mock;

  beforeAll(() => {
    windowOpenPopup = jest.fn().mockReturnValue(popup);
    Object.defineProperty(globalThis, 'window', {value: {open: windowOpenPopup}});
  });

  beforeEach(() => {
    popup.location.href = '';
    (popup as any).closed = false;
    windowOpenPopup.mockReset();
    windowOpenPopup.mockReturnValue(popup);

    TestBed.configureTestingModule({
      imports: [
        HelpLinkComponent,
      ],
    });

    fixture = TestBed.createComponent(HelpLinkComponent);
    component = fixture.componentInstance;
    component.href = 'https://test.domain.com';
    component.target = 'popup';

    preventDefault = jest.fn();
    stopImmediatePropagation = jest.fn();
  });

  afterAll(() => {
    Object.defineProperty(globalThis, 'window', {value: originalLocation});
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('openPopup()', () => {
    it('should return true if target is set to a new tab', () => {
      component.target = '_blank';
      expect(component.openPopup({} as any)).toBeTruthy();
    });

    it('should prevent default behavior of the click event', () => {
      component.openPopup({preventDefault, stopImmediatePropagation} as any);
      expect(preventDefault).toBeCalledTimes(1);
    });

    it('should prevent stop propgation of the click event', () => {
      component.openPopup({preventDefault, stopImmediatePropagation} as any);
      expect(stopImmediatePropagation).toBeCalledTimes(1);
    });

    it('should set the popup location', () => {
      component.openPopup({preventDefault, stopImmediatePropagation} as any);
      expect(popup.location.href).toEqual(component.href);
    });

    it('should save a reference to the popup for reusing', () => {
      component.openPopup({preventDefault, stopImmediatePropagation} as any);
      expect((window as any).DatakitchenHelpPopup).toBe(popup);
    });

    it('should reuse a previous opened popup', () => {
      (window as any).DatakitchenHelpPopup = popup;

      component.openPopup({preventDefault, stopImmediatePropagation} as any);
      expect(windowOpenPopup).not.toBeCalled();
    });

    it('should open a new one instead of reusing a closed popup', () => {
      (popup as any).closed = true;
      (window as any).DatakitchenHelpPopup = popup;

      component.openPopup({preventDefault, stopImmediatePropagation} as any);
      expect(windowOpenPopup).toBeCalledTimes(1);
    });
  });
});
