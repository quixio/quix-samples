import { throttleTime, map, Observable, OperatorFunction, tap } from 'rxjs';

export function bufferThrottleTime<T>(time: number = 0): OperatorFunction<T, T[]> {
  return (source: Observable<T>) => {
    let bufferedValues: T[] = [];

    return source.pipe(
      tap(value => bufferedValues.push(value)),
      throttleTime(time),
      map(() => bufferedValues),
      tap(() => bufferedValues = []),
    );
  };
}