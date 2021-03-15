import React, { Component } from "react";
import { render } from  "react-dom"

export default class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (<h1>This is a React component!</h1>);
    }
}

// Finds elements with id of div and renders the above App class within them
const appDiv = document.getElementById("app");
render(<App />, appDiv);