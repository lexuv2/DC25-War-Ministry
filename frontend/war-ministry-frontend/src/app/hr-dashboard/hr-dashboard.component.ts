import { Component, inject, TemplateRef, ViewChild } from '@angular/core';
import { Breakpoints, BreakpointObserver } from '@angular/cdk/layout';
import { map } from 'rxjs/operators';
import { AsyncPipe, CommonModule } from '@angular/common';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-hr-dashboard',
  templateUrl: './hr-dashboard.component.html',
  styleUrl: './hr-dashboard.component.scss',
  imports: [
    AsyncPipe,
    MatGridListModule,
    MatMenuModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    CommonModule
  ]
})
export class HrDashboardComponent {
  private breakpointObserver = inject(BreakpointObserver);

  /** Based on the screen size, switch from standard to one column per row */
  cards!: Observable<Array<{ title: string; cols: number; rows: number; template: TemplateRef<any> }>>;

@ViewChild('card1', { static: true }) card1!: TemplateRef<any>;
@ViewChild('card3', { static: true }) card3!: TemplateRef<any>;
@ViewChild('card4', { static: true }) card4!: TemplateRef<any>;

ngOnInit() {
  this.cards = this.breakpointObserver.observe(Breakpoints.Handset).pipe(
    map(({ matches }) => {
      if (matches) {
        return [
          { title: 'Witaj', cols: 1, rows: 1, template: this.card1 },
          { title: 'Nasze wartości', cols: 1, rows: 1, template: this.card3 },
          { title: 'Kontakt', cols: 1, rows: 1, template: this.card4 }
        ];
      }
      return [
        { title: 'Witaj', cols: 1, rows: 1, template: this.card1 },
        { title: 'Nasze wartości', cols: 1, rows: 1, template: this.card3 },
        { title: 'Kontakt', cols: 1, rows: 1, template: this.card4 }
      ];
    })
  );
}

}
