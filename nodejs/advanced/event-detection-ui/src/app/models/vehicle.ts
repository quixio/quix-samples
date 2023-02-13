import { EventData } from "./eventData";

export interface Vehicle {
  latitude?: number;
  longitude?: number;
  altitude?: number;
  heading?: number;
  speed?: number;
  batteryLevel?: number;
  accuracy?: number;
  lastPosition?: Date;
  name?: string;
  color?: string;
  wear?: number;
  tail?: { lat: number, lng: number }[];
  alerts?: {
    data: EventData[],
    position: Position[]
  };
}

export interface Position { latitude: number, longitude: number }; 