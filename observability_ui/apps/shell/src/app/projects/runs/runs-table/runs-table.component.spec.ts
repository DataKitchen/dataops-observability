import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockModule } from 'ng-mocks';
import { TableWrapperModule } from '@observability-ui/ui';
import { RunsTableComponent } from './runs-table.component';
import { TranslationModule } from '@observability-ui/translate';

describe('RunsTableComponent', () => {
  let component: RunsTableComponent;
  let fixture: ComponentFixture<RunsTableComponent>;


  beforeEach(async () => {

    await TestBed.configureTestingModule({
      declarations: [ RunsTableComponent ],
      imports: [ MockModule(TableWrapperModule), MockModule(TranslationModule) ]
    }).compileComponents();


    fixture = TestBed.createComponent(RunsTableComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
