import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatNavList } from '@angular/material/list';
import { RouterTestingModule } from '@angular/router/testing';
import { MockComponent } from 'ng-mocks';

import { SidenavMenuComponent } from './sidenav-menu.component';
import { DynamicComponentModule } from '@observability-ui/ui';

describe('SidenavMenuComponent', () => {
  let component: SidenavMenuComponent;
  let fixture: ComponentFixture<SidenavMenuComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        SidenavMenuComponent,
        MockComponent(MatNavList),
      ],
      imports: [
        RouterTestingModule,
        DynamicComponentModule,
      ],

    })
    .compileComponents();

    fixture = TestBed.createComponent(SidenavMenuComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
