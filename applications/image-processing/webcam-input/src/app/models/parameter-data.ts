/// <summary>
/// Describes parameter data for multiple timestamps
/// </summary>
export class ParameterData {
  /// <summary>
  /// Topic Name source of the generated the package
  /// </summary>
  topicName: string;

  /// <summary>
  /// Stream Id source of the generated the package
  /// </summary>
  streamId: string;

  /// <summary>
  /// The unix epoch from, which all other timestamps in this model are measured from in nanoseconds.
  /// 0 = UNIX epoch (01/01/1970)
  /// </summary>
  epoch: number;

  /// <summary>
  /// The timestamps of values in nanoseconds since <see cref="Epoch"/>.
  /// Timestamps are matched by index to <see cref="NumericValues"/>, <see cref="StringValues"/> and <see cref="TagValues"/>
  /// </summary>
  timestamps: number[];

  /// <summary>
  /// The numeric values for parameters.
  /// The key is the parameter Id the values belong to
  /// The value is the numerical values of the parameter. Values are matched by index to <see cref="Timestamps"/>
  /// </summary>
  numericValues: { [key: string]: number[] };

  /// <summary>
  /// The string values for parameters.
  /// The key is the parameter Id the values belong to
  /// The value is the string values of the parameter. Values are matched by index to <see cref="Timestamps"/>
  /// </summary>
  stringValues: { [key: string]: string[] };
  binaryValues: { [key: string]: number[] };


  /// <summary>
  /// The tag values for parameters.
  /// The key is the parameter Id the values belong to
  /// The value is the tag values of the parameter. Values are matched by index to <see cref="Timestamps"/>
  /// </summary>
  tagValues: { [key: string]: string[] };
}