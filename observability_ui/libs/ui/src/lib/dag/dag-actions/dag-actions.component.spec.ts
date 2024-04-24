import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatIcon } from '@angular/material/icon';
import { TranslatePipeMock } from '@observability-ui/translate';
import { MockComponent } from 'ng-mocks';
import { DagActionsComponent } from './dag-actions.component';

describe('DAG Actions Component', () => {
  let component: DagActionsComponent;
  let fixture: ComponentFixture<DagActionsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ ],
      declarations: [ DagActionsComponent, TranslatePipeMock, MockComponent(MatIcon) ],
      providers: [],
    });

    fixture = TestBed.createComponent(DagActionsComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
