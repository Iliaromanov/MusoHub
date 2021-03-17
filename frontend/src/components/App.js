import React, { Component } from "react";
import { render } from  "react-dom";
import HomePage from "./HomePage";


// First component, usually called App, is the entry component
export default class App extends Component { 
    constructor(props) {
        super(props);
    }

    render() {
        return (
        <div className="center">
            <HomePage />
        </div>);
    }
}

// Finds elements with id of div and renders the above App class within them
const appDiv = document.getElementById("app");
render(<App  />, appDiv); 