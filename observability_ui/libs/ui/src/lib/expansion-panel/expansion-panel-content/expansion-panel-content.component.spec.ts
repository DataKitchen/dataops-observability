import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ExpansionPanelContentComponent } from './expansion-panel-content.component';

describe('expansion-panel-content', () => {

  let component: ExpansionPanelContentComponent;
  let fixture: ComponentFixture<ExpansionPanelContentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExpansionPanelContentComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(ExpansionPanelContentComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
