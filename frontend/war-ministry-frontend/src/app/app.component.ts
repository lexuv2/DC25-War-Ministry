import { Component } from '@angular/core';
import { NavbarComponent } from './navbar/navbar.component';
import { ClickBoomDirective } from './click-boom.directive';

@Component({
  selector: 'app-root',
  imports: [NavbarComponent, ClickBoomDirective],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'war-ministry-frontend';
}
