import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JourneysListComponent } from './journeys-list.component';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { EMPTY, of } from 'rxjs';
import { AddJourneyDialogComponent } from '../add-journey-dialog/add-journey-dialog.component';
import { MockProviders } from 'ng-mocks';
import { JourneysStore } from '../journeys.store';
import { JourneysService } from '../../../services/journeys/journeys.service';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { Project, ProjectStore } from '@observability-ui/core';
import { ActivatedRoute } from '@angular/router';
import { ComponentStore } from '../../components/components.store';

describe('JourneysListComponent', () => {
  let component: JourneysListComponent;
  let fixture: ComponentFixture<JourneysListComponent>;
  let matDialog: MatDialog;

  const mockProject = { id: '43221' } as Project;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ JourneysListComponent ],
      providers: [
        MockProviders(MatDialog, JourneysService),
        MockProvider(ProjectStore, class {
          current$ = of(mockProject);
        }),
        MockProvider(JourneysStore, class {
          list$ = of([]);
          getLoadingFor = () => of(false);
        }),
        MockProvider(ComponentStore, class {
          list$ = of([]);
        }),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              queryParams: {}
            }
          },
        },
      ]
    }).compileComponents();

    matDialog = TestBed.inject(MatDialog);
    matDialog.open = jest.fn().mockImplementation(() => {
      return { afterClosed: () => EMPTY };
    });

    fixture = TestBed.createComponent(JourneysListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('openAddJourneyDialog', () => {
    it('should open dialog with correct parameters', () => {
      component.openAddJourneyDialog();
      expect(matDialog.open).toHaveBeenCalledWith(AddJourneyDialogComponent, expect.objectContaining({
        width: '600px',
        autoFocus: false
      }));
    });
  });
});
