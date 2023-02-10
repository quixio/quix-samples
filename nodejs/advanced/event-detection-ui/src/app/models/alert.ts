export interface Alert {
  title?: string,
  streamId?: string,
  color?: 'primary' | 'accent' | 'warn',
  icon?: string,
  timestamp?: number;
}