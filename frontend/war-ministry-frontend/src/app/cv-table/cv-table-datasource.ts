import { DataSource } from '@angular/cdk/collections';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { catchError, map } from 'rxjs/operators';
import { Observable, BehaviorSubject, merge, of } from 'rxjs';
import { CvService } from '../cv/cv.service';

// TODO: Replace this with your own data model type
export interface CvTableItem {
  id: string;
  name: string;
  position_applied: string;
  score: number;
  status: string;
}

/**
 * Data source for the CvTable view. This class should
 * encapsulate all logic for fetching and manipulating the displayed data
 * (including sorting, pagination, and filtering).
 */
export class CvTableDataSource extends DataSource<CvTableItem> {
  data: CvTableItem[] = [];
  paginator: MatPaginator | undefined;
  sort: MatSort | undefined;
  error$ = new BehaviorSubject<string | null>(null);

  constructor(private cvService: CvService) {
    super();
  }

  /**
   * Connect this data source to the table. The table will only update when
   * the returned stream emits new items.
   * @returns A stream of the items to be rendered.
   */
  connect(): Observable<CvTableItem[]> {
    if (!this.paginator || !this.sort) {
      throw Error('Please set the paginator and sort on the data source before connecting.');
    }

    // Combine everything that affects the rendered data into one update
    // stream for the data-table to consume.
    return merge(
      this.cvService.getCvList().pipe(
        map(items => {
          this.error$.next(null);
          this.data = items;
          return items;
        }),
        catchError(() => {
          this.error$.next('Błąd pobierania danych, spróbuj ponownie później.');
          this.data = [];
          return of([]);
        })
      ),
      this.paginator.page,
      this.sort.sortChange
    ).pipe(
      map(() => this.getPagedData(this.getSortedData([...this.data])))
    );
  }

  /**
   *  Called when the table is being destroyed. Use this function, to clean up
   * any open connections or free any held resources that were set up during connect.
   */
  disconnect(): void {
    this.error$.complete();
  }

  /**
   * Paginate the data (client-side). If you're using server-side pagination,
   * this would be replaced by requesting the appropriate data from the server.
   */
  private getPagedData(data: CvTableItem[]): CvTableItem[] {
    if (this.paginator) {
      const startIndex = this.paginator.pageIndex * this.paginator.pageSize;
      return data.splice(startIndex, this.paginator.pageSize);
    } else {
      return data;
    }
  }

  /**
   * Sort the data (client-side). If you're using server-side sorting,
   * this would be replaced by requesting the appropriate data from the server.
   */
  private getSortedData(data: CvTableItem[]): CvTableItem[] {
    if (!this.sort || !this.sort.active || this.sort.direction === '') {
      return data;
    }

    return data.sort((a, b) => {
      const isAsc = this.sort?.direction === 'asc';
      switch (this.sort?.active) {
        case 'name': return compare(a.name, b.name, isAsc);
        case 'id': return compare(+a.id, +b.id, isAsc);
        case 'score': return compare(a.score, b.score, isAsc);
        case 'position_applied': return compare(a.position_applied, b.position_applied, isAsc);
        default: return 0;
      }
    });
  }
}

/** Simple sort comparator for example ID/Name columns (for client-side sorting). */
function compare(a: string | number, b: string | number, isAsc: boolean): number {
  return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
}
