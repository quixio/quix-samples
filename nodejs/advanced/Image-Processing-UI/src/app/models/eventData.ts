import { EventValue } from './eventValue';

export interface EventData {
    /**
     * The event data
     */
    data?: { [key: string]: Array<EventValue>; };
}