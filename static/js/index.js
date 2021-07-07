import React from "react"
import ReactDOM from "react-dom"

import { UtcClock } from "./UtcClock";
import { GndApp } from "./GndApp";

import { whenMapsLoaded, initMap } from "./map"

whenMapsLoaded(initMap);

ReactDOM.render(
    <UtcClock/>,
    document.getElementById("header-time-wrapper")
);
ReactDOM.render(
    <GndApp/>,
    document.getElementById("gnd-app")
);
