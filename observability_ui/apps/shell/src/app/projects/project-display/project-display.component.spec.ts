import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProjectDisplayComponent } from './project-display.component';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { Project, ProjectStore } from '@observability-ui/core';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs';

describe('project-display', () => {

  let component: ProjectDisplayComponent;
  let fixture: ComponentFixture<ProjectDisplayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule,
      ],
      declarations: [ ProjectDisplayComponent ],
      providers: [
        MockProvider(ProjectStore, class {
          current$ = of({id: 'project_id'} as Project);
          list$ = of([{id: 'project_id'}, {id: 'other_project'}]);
          loading$ = of({});
          getLoadingFor = () => of({});
        }),
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ProjectDisplayComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
