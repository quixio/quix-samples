import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';
import { QuixLiveService } from './services/quix.ts';
import {Data} from '../src/Models/data.ts'

function App() {
  const [activeStreams, setActiveStreams] = useState([]);
  const [event, setEvent] = useState(null);
  const [data, setData] = useState(null);
  const [inputValue, setInputValue] = useState(''); // new state for input value
  const [quixInputTopic, setQuixInputTopic] = useState(''); // new state for input value
  const [quixLiveService, setQuixLiveService] = useState(null); // new state for input value

  const onActiveStreamsChanged = (stream, action) => {
    console.log("Active streams changed " + stream.streamId)
    setActiveStreams(prevStreams => [...prevStreams, stream]);
  };

  const eventReceived = (event) => {
    setEvent(event); // set the state here
  };
  
  const dataReceived = (data) => {
    setData(data); // set the state here
  };

  const handleSendData = async () => { // new function to handle button click

    let dataObject = {
      timestamps: [Date.now() * 1000000], // Array with a single timestamp
      stringValues: {
          "ReactMessage": [inputValue] // Dictionary with a single key-value pair
      }
  };

    await quixLiveService.sendParameterData(quixInputTopic, "react-messages-stream", dataObject);
  };

  useEffect(() => {

    const startAndSubscribe = async () => {
      // Create an instance of QuixLiveService
      const quixService = new QuixLiveService();
      
      await quixService.getWorkspaceIdAndToken();
      await quixService.startConnection();

      const inputTopicPromise = await quixService.fetchConfig("input_topic"); //comment this if using manual topic

      /*NOTE -- If working locally you'll need to set the input topic manually*/
      //const inputTopic = "hello-world-source";
      const inputTopic = inputTopicPromise.value;

      setQuixInputTopic(inputTopic);

      console.log("Done starting")

      quixService.subscribeToActiveStreams(onActiveStreamsChanged, inputTopic);
      quixService.subscribeToEvents(eventReceived, inputTopic, "*", "*");
      quixService.subscribeToParameterData(dataReceived, inputTopic, "*", "*");

      setQuixLiveService(quixService);
    };
    startAndSubscribe();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        
        <div>
          <p style={{fontSize: '14px'}}>Send a string value to the <b>{quixInputTopic}</b> with this form. <br/>The message will be displayed in the `Live Data` below.</p>
          <input 
            type="text" 
            value={inputValue} 
            onChange={e => setInputValue(e.target.value)} 
          />
          <button onClick={handleSendData}>Send Data</button>
        </div>

        <div style={{ display: 'flex', margin: '10px' }}>


          <div style={{ border: '1px solid black', flex: 1 }}>
            <h4>Active Streams</h4>
            <div style={{ maxWidth: '300px', maxHeight: '500px', overflowY: 'auto' }}>
              {activeStreams.reverse().map((stream, index) => (
                <div key={index} style={{ fontSize: '10px' }}>
                  <p>Stream ID: {stream.streamId}</p>
                  <p>Name: {stream.name}</p>
                </div>
              ))}
            </div>
          </div>
          
          <div style={{ border: '1px solid blue', flex: 1 }}>
            <h4>Live data</h4>
            <div>
              {data && (
                <div style={{ fontSize: '20px' }}>
                  <p>Topic ID: {data?.topicId}</p>
                  <div>
                    <h4>Numeric Values</h4>
                    {data?.numericValues && Object.entries(data.numericValues).map(([key, value], index) => (
                      <p key={index}>{key}: {value.join(', ')}</p>
                    ))}
                  </div>

                  <div>
                    <h4>String Values</h4>
                    {data?.stringValues && Object.entries(data.stringValues).map(([key, value], index) => (
                      <p key={index}>{key}: {value.join(', ')}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div style={{ border: '1px solid orange', flex: 1 }}>
            <h4>Events</h4>
            <div>
              {event && (
                <div style={{ fontSize: '20px' }}>
                  <p>Event Id: {event?.id}</p>
                  <p>Event Value: {event?.value}</p>
                </div>
              )}
            </div>
          </div>

        </div>

      </header>
    </div>
  );
}

export default App;