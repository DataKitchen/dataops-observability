import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EntryComponent } from './entry.component';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ProjectStore } from '@observability-ui/core';
import { of } from 'rxjs';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MockComponent } from 'ng-mocks';

describe('shell-entry', () => {

  let component: EntryComponent;
  let fixture: ComponentFixture<EntryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        EntryComponent,
        MockComponent(MatProgressSpinner),
      ],
      providers: [
        MockProvider(ProjectStore, class {
          current$ = of({id: 'project_id'});
        }),
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(EntryComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
