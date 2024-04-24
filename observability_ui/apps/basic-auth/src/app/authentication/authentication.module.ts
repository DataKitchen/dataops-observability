import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { AuthenticationComponent } from './authentication.component';
import { remoteRoutes } from './authentication.routes';
import { SessionService } from '@observability-ui/core';
import { BasicAuthService } from '../services/auth.service';

@NgModule({
  declarations: [
    AuthenticationComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(remoteRoutes),
  ],
  providers: [
    { provide: SessionService, useClass: BasicAuthService },
  ],
})
export class AuthenticationModule {}
