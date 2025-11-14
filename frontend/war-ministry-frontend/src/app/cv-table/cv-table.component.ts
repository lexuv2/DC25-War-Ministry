import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { MatTableModule, MatTable } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CvTableDataSource, CvTableItem } from './cv-table-datasource';
import { RouterModule } from '@angular/router';
import { CvService } from '../cv/cv.service';

@Component({
  selector: 'app-cv-table',
  templateUrl: './cv-table.component.html',
  styleUrl: './cv-table.component.scss',
  imports: [MatTableModule, MatPaginatorModule, MatSortModule, MatSnackBarModule, RouterModule]
})
export class CvTableComponent implements AfterViewInit {
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;
  @ViewChild(MatTable) table!: MatTable<CvTableItem>;
  dataSource : CvTableDataSource;
  errorMessage: string | null = null;

  /** Columns displayed in the table. Columns IDs can be added, removed, or reordered. */
  displayedColumns = ['name', 'date_received', 'position_applied', 'score', 'status', 'view_more'];

  constructor(private cvService: CvService, private snackBar: MatSnackBar) {
    this.dataSource = new CvTableDataSource(this.cvService);
  }

  ngAfterViewInit(): void {
    this.dataSource.sort = this.sort;
    this.dataSource.paginator = this.paginator;
    this.table.dataSource = this.dataSource;

    this.dataSource.error$.subscribe(msg => {
      if (msg) {
        this.snackBar.open(msg, 'Zamknij', {
          duration: 10000,
        });
      }
    });
  }
}
