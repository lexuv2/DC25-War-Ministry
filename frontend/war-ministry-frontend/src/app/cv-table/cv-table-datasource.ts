import { DataSource } from '@angular/cdk/collections';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { map } from 'rxjs/operators';
import { Observable, of as observableOf, merge } from 'rxjs';

// TODO: Replace this with your own data model type
export interface CvTableItem {
  id: number;
  name: string;
  date_received: Date;
  position_applied: string;
  score: number;
  status: string;
}

// TODO: replace this with real data from your application
const EXAMPLE_DATA: CvTableItem[] = [
  {id: 1, name: 'Malwina Kosewska', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 2, name: 'Kamil Nietupski', date_received: new Date(), position_applied: 'Żołnierz piechoty zmechanizowanej', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 3, name: 'Tobiasz Bączyński', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 4, name: 'Karol Dobrzycki', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 5, name: 'Marcel Ziętal', date_received: new Date(), position_applied: 'Żołnierz piechoty zmechanizowanej', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 6, name: 'Bronisław Laskus', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 7, name: 'Sylwia Herdzik', date_received: new Date(), position_applied: 'Żołnierz piechoty zmechanizowanej', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 8, name: 'Apolonia Rembowska', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 9, name: 'Mirosław Kyc', date_received: new Date(), position_applied: 'Żołnierz piechoty zmechanizowanej', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 10, name: 'Teodor Krysiak', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 11, name: 'Karina Wcisło', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 12, name: 'Zdzisław Mączkowski', date_received: new Date(), position_applied: 'Żołnierz piechoty zmechanizowanej', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 13, name: 'Wiktoria Wieczorkiewicz', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 14, name: 'Rudolf Grenda', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 15, name: 'Eugeniusz Rychcik', date_received: new Date(), position_applied: 'Żołnierz piechoty zmechanizowanej', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 16, name: 'Eryk Polakowski', date_received: new Date(), position_applied: 'Żołnierz piechoty zmechanizowanej', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 17, name: 'Wiesław Benedyk', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 18, name: 'Antoni Szelest', date_received: new Date(), position_applied: 'Żołnierz piechoty zmechanizowanej', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 19, name: 'Magda Pacyga', date_received: new Date(), position_applied: 'Operator wajchy', score: Math.floor(Math.random() * 1000), status: 'unknown'},
  {id: 20, name: 'Daria Średnicka', date_received: new Date(), position_applied: 'Żołnierz piechoty zmechanizowanej', score: Math.floor(Math.random() * 1000), status: 'unknown'},
];

/**
 * Data source for the CvTable view. This class should
 * encapsulate all logic for fetching and manipulating the displayed data
 * (including sorting, pagination, and filtering).
 */
export class CvTableDataSource extends DataSource<CvTableItem> {
  data: CvTableItem[] = EXAMPLE_DATA;
  paginator: MatPaginator | undefined;
  sort: MatSort | undefined;

  constructor() {
    super();
  }

  /**
   * Connect this data source to the table. The table will only update when
   * the returned stream emits new items.
   * @returns A stream of the items to be rendered.
   */
  connect(): Observable<CvTableItem[]> {
    if (this.paginator && this.sort) {
      // Combine everything that affects the rendered data into one update
      // stream for the data-table to consume.
      return merge(observableOf(this.data), this.paginator.page, this.sort.sortChange)
        .pipe(map(() => {
          return this.getPagedData(this.getSortedData([...this.data ]));
        }));
    } else {
      throw Error('Please set the paginator and sort on the data source before connecting.');
    }
  }

  /**
   *  Called when the table is being destroyed. Use this function, to clean up
   * any open connections or free any held resources that were set up during connect.
   */
  disconnect(): void {}

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
