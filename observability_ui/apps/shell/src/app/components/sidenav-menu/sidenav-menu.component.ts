import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { map, Observable } from 'rxjs';
import { Menu } from './sidenav-menu.model';

@Component({
  selector: 'shell-sidenav-menu',
  templateUrl: 'sidenav-menu.component.html',
  styleUrls: [ 'sidenav-menu.component.scss' ],
})
export class SidenavMenuComponent {
  readonly menus$: Observable<Array<Menu>> = this.route.data.pipe(
    map((data) => data['menus'] as Array<Menu>),
  );
  readonly baseRoute: ActivatedRoute | null = this.route.parent;

  constructor(
    private route: ActivatedRoute,
  ) {
  }
}
