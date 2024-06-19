import { Component } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { map, Observable } from 'rxjs';
import { Menu } from './sidenav-menu.model';
import { AsyncPipe, NgFor, NgIf } from '@angular/common';
import { MatLegacyListModule } from '@angular/material/legacy-list';
import { MatIconModule } from '@angular/material/icon';
import { DynamicComponentModule } from '@observability-ui/ui';

@Component({
  selector: 'shell-sidenav-menu',
  templateUrl: 'sidenav-menu.component.html',
  styleUrls: [ 'sidenav-menu.component.scss' ],
  imports: [
    NgIf,
    NgFor,
    AsyncPipe,
    RouterModule,
    MatIconModule,
    MatLegacyListModule,
    DynamicComponentModule,
  ],
  standalone: true,
})
export class SidenavMenuComponent {
  readonly menus$: Observable<Array<Menu>> = this.route.data.pipe(
    map((data) => data['menus'] as Array<Menu>),
  );
  readonly baseRoute$: Observable<ActivatedRoute | null> = this.route.data.pipe(
    map((data) => data['baseRouteCallback']?.(this.route) ?? this.route.parent),
  );

  constructor(
    private route: ActivatedRoute,
  ) {
  }
}
