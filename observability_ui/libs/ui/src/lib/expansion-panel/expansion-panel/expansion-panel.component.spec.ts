import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ExpansionPanelComponent } from './expansion-panel.component';
import { MockComponent } from 'ng-mocks';
import { MatIcon } from '@angular/material/icon';

describe('expansion-panel', () => {

  let component: ExpansionPanelComponent;
  let fixture: ComponentFixture<ExpansionPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        ExpansionPanelComponent,
        MockComponent(MatIcon),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ExpansionPanelComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });



});
