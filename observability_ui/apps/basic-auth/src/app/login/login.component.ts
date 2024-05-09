import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { MatLegacyCardModule } from '@angular/material/legacy-card';
import { BasicAuthService } from '../services/auth.service';
import { AlertComponent, TextFieldModule } from '@observability-ui/ui';
import { ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { take } from 'rxjs';
import { TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';

@Component({
  selector: 'auth-login',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatLegacyButtonModule,
    MatLegacyCardModule,
    ReactiveFormsModule,
    RouterModule,

    AlertComponent,
    TextFieldModule,
  ],
  templateUrl: './login.component.html',
  styleUrls: [ './login.component.scss' ],
})
export class LoginComponent {
  router = inject(Router);
  authService = inject(BasicAuthService);

  form = new TypedFormGroup<{ username: string; password: string; }>({
    username: new TypedFormControl<string>(''),
    password: new TypedFormControl<string>(''),
  });

  loginError: undefined | string;

  login(): void {
    this.loginError = undefined;
    this.authService.login(this.form.value).pipe(
      take(1),
    ).subscribe({
      next: (url) => this.router.navigateByUrl(url),
      error: (error) => {
        this.loginError = error.error?.error || (error.status === 0 ? 'Unable to reach Observability API.' : error.message);
        console.error(error);
      },
    });
  }
}
