import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JourneyDetailsComponent } from './journey-details.component';
import { ActivatedRoute } from '@angular/router';
import { JourneysStore } from '../journeys.store';
import { of } from 'rxjs';
import { MockComponents, MockDirective, MockModule, MockProvider } from 'ng-mocks';
import { RouterTestingModule } from '@angular/router/testing';
import { TranslationModule } from '@observability-ui/translate';
import { DetailsHeaderComponent } from '@observability-ui/ui';
import { MatLegacyTabLink as MatTabLink, MatLegacyTabNav as MatTabNav, MatLegacyTabNavPanel as MatTabNavPanel } from '@angular/material/legacy-tabs';
import { BaseComponent } from '@observability-ui/core';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { MatIconModule } from '@angular/material/icon';

describe('JourneyDetailsComponent', () => {
  let component: JourneyDetailsComponent;
  let fixture: ComponentFixture<JourneyDetailsComponent>;

  let journeysStore: JourneysStore;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ JourneyDetailsComponent, MockComponents(DetailsHeaderComponent, MatTabNavPanel, MatTabNav), MockDirective(MatTabLink) ],
      imports: [
        RouterTestingModule,
        MatIconModule,
        MockModule(TranslationModule),
        MockModule(MatIconModule),
      ],
      providers: [
        MockProvider(ActivatedRoute, {
          params: of({ id: '1' })
        }),
        MockProvider(JourneysStore, {
          components$: of([ { key: 'A' }, { key: 'C' }, { key: 'B' } ] as BaseComponent[]),
          getEntity: jest.fn(),
          dispatch: jest.fn(),
        }),
      ]
    }).compileComponents();

    journeysStore = TestBed.inject(JourneysStore);

    fixture = TestBed.createComponent(JourneyDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should call getEntity from the store', () => {
    expect(journeysStore.getEntity).toHaveBeenCalledWith('1');
  });

  it('should get the journey components', () => {
    expect(journeysStore.dispatch).toHaveBeenCalledWith('findComponents', '1');
  });

  it('should have a comma separated list of the component keys', () => {
    new TestScheduler().run(({ expectObservable }) => {
      expectObservable(component.componentKeys$).toBe('(a|)', { a: 'A,C,B' });
    });
  });
});
