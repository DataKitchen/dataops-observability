import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ExpansionPanelTitleComponent } from './expansion-panel-title.component';

describe('expansion-panel-title', () => {

  let component: ExpansionPanelTitleComponent;
  let fixture: ComponentFixture<ExpansionPanelTitleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExpansionPanelTitleComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(ExpansionPanelTitleComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
