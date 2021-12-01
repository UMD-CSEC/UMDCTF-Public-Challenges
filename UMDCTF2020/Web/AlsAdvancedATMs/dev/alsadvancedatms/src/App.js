import React from 'react';
import { BrowserRouter, Route, Switch } from "react-router-dom";
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import MainPage from './main/main-page.js';
import Secret from './secret/secret.js';
import PageNotFound from './main/page-not-found.js';

function App() {
  return (
    <BrowserRouter basename='/'>
      <Switch>
        <Route exact path="/" component={MainPage} />
        <Route path="/eonline" component={Secret} />
        <Route component={PageNotFound} />
      </Switch>
    </BrowserRouter>
  );
}

export default App;
