/**
 * Telemetry Query API
 * No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)
 *
 * OpenAPI spec version: v1
 *
 *
 * NOTE: This class is auto generated by the swagger code generator program.
 * https://github.com/swagger-api/swagger-codegen.git
 * Do not edit the class manually.
 */

/**
 * Describes properties of a stream
 */
export interface Stream {
  /**
   * The primary identifier of the stream
   */
  streamId?: string;
  /**
   * The display name of the stream
   */
  name?: string;
  /**
   * The topic the stream originates from
   */
  topic?: string;
  /**
   * The time the stream was created at
   */
  createdAt?: Date;
  /**
   * The time the stream was last updated at
   */
  lastUpdate?: Date;
  /**
   * Time of the recording. Optional.
   */
  timeOfRecording?: Date;
  /**
   * The earliest data within the session in unix nanoseconds
   */
  dataStart?: number;
  /**
   * The last data within the session in unix nanoseconds
   */
  dataEnd?: number;
  /**
   * The sate of the stream
   */
  status?: StreamStatus;
  /**
   * Metadata (extra context) for the stream
   */
  metadata?: { [key: string]: string; };
  /**
   * The stream Ids this session is derived from.
   */
  parents?: Array<string>;
  /**
   * The location of the stream
   */
  location?: string;

  children?: Stream[];
}

export type StreamStatus = 'Open' | 'Closed' | 'Aborted' | 'Terminated' | 'Interrupted' | 'Deleting';

export const StreamStatus = {
  Open: 'Open' as StreamStatus,
  Closed: 'Closed' as StreamStatus,
  Aborted: 'Aborted' as StreamStatus,
  Terminated: 'Terminated' as StreamStatus,
  Interrupted: 'Interrupted' as StreamStatus,
  Deleting: 'Deleting' as StreamStatus,
};