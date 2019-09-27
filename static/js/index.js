import React from "react"
import ReactDOM from "react-dom"

import { UtcClock } from "./UtcClock";
import { GndApp } from "./GndApp";

import * as map from "./map"

// Make this global so the GMaps API can see it.
windown.initMap = map.initMap;

ReactDOM.render(
    <UtcClock/>,
    document.getElementById("header-time-wrapper")
);
ReactDOM.render(
    <GndApp/>,
    document.getElementById("gnd-app")
);
