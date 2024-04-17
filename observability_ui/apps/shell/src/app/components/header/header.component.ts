import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { SessionService, EntitiesResolver } from '@observability-ui/core';
import { CoreComponent } from '@datakitchen/ngx-toolkit';
import { ActivationEnd, Event, Router } from '@angular/router';
import { filter, map, Observable } from 'rxjs';

@Component({
  selector: 'shell-header',
  templateUrl: './header.component.html',
  styleUrls: [ './header.component.scss' ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeaderComponent extends CoreComponent {
  @Input() showMenuToggle = true;
  @Output() toggleMenu: EventEmitter<boolean> = new EventEmitter();

  user$ = this.sessionService.user$;

  private helpWindowFeatures = 'toolbar=0,scrollbars=1,location=0,statusbar=0,menubar=0,resizable=1,width=800,height=600,top=700,left=700';

  helpLink$: Observable<string | undefined> = this.router.events.pipe(
    filter(this.isActivationEnd),
    map((event) => event.snapshot.data),
    filter((data) => data['helpLink']),
    map((data: { helpLink?: string }) => data.helpLink),
  );

  constructor(
    private sessionService: SessionService,
    private entities: EntitiesResolver,
    private router: Router,
  ) {
    super();
  }

  logout() {
    this.sessionService.endSession();
  }

  openSmallHelpWindow(url: string) {
    window.open(`https://docs.datakitchen.io/${url}`, '_blank', this.helpWindowFeatures);
  }

  private isActivationEnd(event: Event): event is ActivationEnd {
    return event instanceof ActivationEnd;
  }
}
