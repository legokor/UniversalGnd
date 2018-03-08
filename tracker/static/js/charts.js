let ctx = document.getElementById("altitudeChart");

charts["altitude"] = new Chart(ctx, {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Altitude (meters)',
            backgroundColor: 'rgba(255, 153, 51, 1)',
            data: [],
        }],
    },
    options: {
        showLines: true,
        title: {
            display: true,
            text: "Altitude",
        }
    }
});

let ctx2 = document.getElementById("speedChart");

charts["speed"] = new Chart(ctx2, {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Speed (meters/second)',
            backgroundColor: 'rgba(255, 153, 51, 1)',
            data: [],
        }],
    },
    options: {
        showLines: true,
        title: {
            display: true,
            text: "Speed",
        }
    }
});
