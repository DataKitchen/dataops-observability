import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { BasicAuthService } from '../services/auth.service';
import { take } from 'rxjs';

@Component({
  selector: 'auth-logout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
  ],
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.scss']
})
export class LogoutComponent implements OnInit {
  private authService = inject(BasicAuthService);

  ngOnInit(): void {
      this.authService.logout().pipe(
        take(1),
      ).subscribe();
  }
}
