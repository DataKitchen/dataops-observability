import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EventsComponent } from './events.component';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ProjectStore } from '@observability-ui/core';
import { of } from 'rxjs';
import { TranslatePipeMock } from '@observability-ui/translate';
import { RouterTestingModule } from '@angular/router/testing';
import { MockComponent } from 'ng-mocks';
import { BreadcrumbComponent } from '@observability-ui/ui';
import { MatLegacyTabsModule as MatTabsModule } from '@angular/material/legacy-tabs';

describe('events', () => {

  let component: EventsComponent;
  let fixture: ComponentFixture<EventsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule,
        MatTabsModule,
      ],
      declarations: [
        EventsComponent,
        TranslatePipeMock,
        MockComponent(BreadcrumbComponent),
      ],
      providers: [
        MockProvider(ProjectStore, class {
          current$ = of({ name: 'project' });
        }),
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(EventsComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
