/**
 * Value details of an event at a given timestamp
 */
export interface EventValue {
    /**
     * Time in nanoseconds since UNIX epoch (01/01/1970)
     */
    timestamp?: number;
    /**
     * Value of the event at this timestamp
     */
    value?: string;
    /**
     * Tags of the event at this timestamp
     */
    tagValues?: { [key: string]: string; };

  topicName: string;
}