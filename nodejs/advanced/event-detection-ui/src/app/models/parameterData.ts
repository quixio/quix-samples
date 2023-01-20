/** Describes parameter data for multiple timestamps */
export interface ParameterData {
	/** Topic Name source of the generated the package */
	topicName: string;

	/** Stream Id source of the generated the package */
	streamId: string;

	/**
	 * The unix epoch from, which all other timestamps in this model are measured from in nanoseconds.
	 * 0 = UNIX epoch (01/01/1970)
	 */
	epoch: number;

	/**
	 * The timestamps of values in nanoseconds since @see Epoch .
	 * Timestamps are matched by index to @see NumericValues , @see StringValues  and @see TagValues
	 */
	timestamps: number[];

	/**
	 * The numeric values for parameters.
	 * The key is the parameter Id the values belong to
	 * The value is the numerical values of the parameter. Values are matched by index to @see Timestamps
	 */
	numericValues: { [key: string]: number[] };

	/**
	 * The string values for parameters.
	 * The key is the parameter Id the values belong to
	 * The value is the string values of the parameter. Values are matched by index to @see Timestamps
	 */
	stringValues: { [key: string]: string[] };

	/**
	 * The tag values for parameters.
	 * The key is the parameter Id the values belong to
	 * The value is the tag values of the parameter. Values are matched by index to @see Timestamps
	 */
	tagValues: { [key: string]: string[] };

	/**
	 * The binary values for parameters.
	 * The key is the parameter Id the values belong to
	 * The value is the binary values of the parameter. Values are matched by index to @see Timestamps
	 */
	binaryValues: { [key: string]: number[][] };
}
