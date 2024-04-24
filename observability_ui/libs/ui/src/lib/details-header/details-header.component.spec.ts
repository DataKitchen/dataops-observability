import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DetailsHeaderComponent } from './details-header.component';

describe('details-header', () => {

  let component: DetailsHeaderComponent;
  let fixture: ComponentFixture<DetailsHeaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DetailsHeaderComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(DetailsHeaderComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
