import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EventsTableComponent } from './events-table.component';
import { MockModule } from 'ng-mocks';
import { MatLegacyDialog as MatDialog, MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { MetadataViewerComponent, TableWrapperModule } from '@observability-ui/ui';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { EventType, EventTypes, TestStatus } from '@observability-ui/core';

describe('EventsTableComponent', () => {
  let component: EventsTableComponent;
  let fixture: ComponentFixture<EventsTableComponent>;

  let dialog: Mocked<MatDialog>;

  const mockEvents: EventType[] = [
    {
      event_type: EventTypes.TestOutcomesEvent,
      raw_data: {
        test_outcomes: [
          { name: 'test_1', description: 'description_1', status: TestStatus.Failed },
          { name: 'test_2', description: 'description_2', status: TestStatus.Failed },
          { name: 'test_3', description: 'description_3', status: TestStatus.Warning },
          { name: 'test_4', description: 'description_4', status: TestStatus.Passed },
        ]
      }
    } as EventType
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EventsTableComponent ],
      providers: [ MockProvider(MatDialog) ],
      imports: [ MockModule(MatDialogModule), MockModule(TableWrapperModule) ]
    }).compileComponents();

    dialog = TestBed.inject(MatDialog) as Mocked<MatDialog>;

    fixture = TestBed.createComponent(EventsTableComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('viewMetadata()', () => {
    const task_name = 'A';
    const event_timestamp = new Date('2022-08-09T15:39:33.983900+00:00');

    const metadata = { name: 'a', description: 'something' };

    it('should open the dialog with the event\'s metadata', () => {
      component.viewMetadata({
        event_type: EventTypes.MessageLogEvent,
        timestamp: event_timestamp,
        raw_data: {
          task_name,
          metadata
        }
      } as unknown as EventType);
      expect(dialog.open).toBeCalledWith(MetadataViewerComponent, expect.objectContaining({
        data: {
          title: 'Event Data',
          all: {
            event_type: EventTypes.MessageLogEvent,
            timestamp: event_timestamp,
            raw_data: {
              task_name,
              metadata
            }
          },
          timestamp: event_timestamp,
          metadata: metadata,
        }
      }));
    });
  });

  describe('getEventsWithTestSummary', () => {
    it('should add test summary to the event if the event_type is TestOutcomesEvent', () => {
      const expectedTestResultsEventSummary = {
        'FAILED': 2,
        'PASSED': 1,
        'TOTAL': 4,
        'WARNING': 1,
      };

      expect((component.getEventsWithTestSummary(mockEvents)[0] as any).summary).toEqual(expectedTestResultsEventSummary);
    });
  });
});
