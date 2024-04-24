import { TestBed } from '@angular/core/testing';
import { ClickListenerService } from './click-listener.service';
import { CommonModule, DOCUMENT } from '@angular/common';

describe('click-listener.service', () => {
  let service: ClickListenerService;
  let document: Document;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ CommonModule ],
      providers: [
        ClickListenerService,
        {
          provide: DOCUMENT,
          useClass: class {
            handler!: (event: Event) => void;

            addEventListener = jest.fn().mockImplementation((_event, handler) => {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
              this.handler = handler;
            });

            dispatchEvent = jest.fn().mockImplementation((event) => {
              this.handler(event);
            });

            querySelectorAll = jest.fn().mockReturnValue([]);
          },
        },
      ],
    }).compileComponents();

    service = TestBed.inject(ClickListenerService);
    document = TestBed.inject(DOCUMENT);
  });

  it('should create', () => {
    expect(service).toBeTruthy();
  });

  it('should listen to click events', () => {
    expect(document.addEventListener).toHaveBeenCalledWith('click', expect.anything());
  });

  it('should notify when a click happens', () => {

    service.onClick.subscribe((event) => {
      expect(event).toBeTruthy();

    });
    document.dispatchEvent(new Event('click'));
  });

});
