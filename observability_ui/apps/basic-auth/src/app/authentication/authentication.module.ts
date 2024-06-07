import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { AuthenticationComponent } from './authentication.component';
import { remoteRoutes } from './authentication.routes';

@NgModule({
  declarations: [
    AuthenticationComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(remoteRoutes),
  ],
  providers: [],
})
export class AuthenticationModule {}
