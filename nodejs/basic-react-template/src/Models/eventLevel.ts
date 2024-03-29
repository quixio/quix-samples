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
 * The event level, describing the severity of the event
 */
export type EventLevel = 'Trace' | 'Debug' | 'Information' | 'Warning' | 'Error' | 'Critical';

export const EventLevel = {
    Trace: 'Trace' as EventLevel,
    Debug: 'Debug' as EventLevel,
    Information: 'Information' as EventLevel,
    Warning: 'Warning' as EventLevel,
    Error: 'Error' as EventLevel,
    Critical: 'Critical' as EventLevel
};