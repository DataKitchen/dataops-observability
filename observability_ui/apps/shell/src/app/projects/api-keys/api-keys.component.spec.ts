import { ComponentFixture, TestBed } from '@angular/core/testing';
import { APIKeysComponent } from './api-keys.component';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ProjectStore } from '@observability-ui/core';
import { of } from 'rxjs';
import { APIKeysStore } from './api-keys.store';
import { ActivatedRoute } from '@angular/router';
import { ActivatedRouteMock } from '@datakitchen/ngx-toolkit';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';

describe('api-keys.component', () => {

  let component: APIKeysComponent;
  let fixture: ComponentFixture<APIKeysComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ APIKeysComponent ],
      providers: [
        MockProvider(ProjectStore, class {
          current$ = of({});
        }),
        MockProvider(APIKeysStore, class {
          list$ = of([]);
          total$ = of(0);
          getLoadingFor = () => of(false);
        }),
        MockProvider(MatDialog),
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock()
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(APIKeysComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
