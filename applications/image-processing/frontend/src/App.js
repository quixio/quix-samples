import logo from './logo.svg';
import './App.css';

import { CreateConnection } from './services/data';
import React, { useEffect, useState } from 'react';

function App() {
  const [data, changeData] = useState({});
  const [dataProcessed, changeProcessedData] = useState({});

  useEffect(() => {
    return CreateConnection(changeData, "{placeholder:topic_raw}");
  }, [changeData]);
  

  useEffect(() => {
    return CreateConnection(changeProcessedData, "{placeholder:topic_processed}");
  }, [changeProcessedData]);

  console.log("element data", data);

  return (
    <div className="App">
      <header className="App-header">
        <h1>CAMERA DATA</h1>
        {data?.image ? <img src={`data:image/png;base64,${data.image}`} /> : "... no image ..."}
        <h1>PROCESSED DATA</h1>
        {data?.image ? <img src={`data:image/png;base64,${dataProcessed.image}`} /> : "... no image ..."}
      </header>
    </div>
  );
}

export default App;
