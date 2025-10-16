import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { MatTableModule, MatTable } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { CvTableDataSource, CvTableItem } from './cv-table-datasource';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-cv-table',
  templateUrl: './cv-table.component.html',
  styleUrl: './cv-table.component.scss',
  imports: [MatTableModule, MatPaginatorModule, MatSortModule, RouterModule]
})
export class CvTableComponent implements AfterViewInit {
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;
  @ViewChild(MatTable) table!: MatTable<CvTableItem>;
  dataSource = new CvTableDataSource();

  /** Columns displayed in the table. Columns IDs can be added, removed, or reordered. */
  displayedColumns = ['id', 'name', 'date_received', 'position_applied', 'score', 'status', 'view_more'];

  ngAfterViewInit(): void {
    this.dataSource.sort = this.sort;
    this.dataSource.paginator = this.paginator;
    this.table.dataSource = this.dataSource;
  }
}
