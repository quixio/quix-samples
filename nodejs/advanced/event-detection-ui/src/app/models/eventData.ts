/** Describes data for a single event */
export interface EventData {
	/** Topic Name source of the generated the package */
	topicName: string;

	/** Stream Id source of the generated the package */
	streamId: string;

	/** The timestamp of events in nanoseconds since unix epoch */
	timestamp: number;

	/** Tags applied to the event */
	tags: { [key: string]: string };

	/** The globally unique identifier of the event */
	id: string;

	/** The value of the event */
	value: string;
}
