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

let ctx2 = document.getElementById("extTempChart");

charts["exttemp"] = new Chart(ctx2, {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'External temperature (Celsius)',
            backgroundColor: 'rgba(255, 153, 51, 1)',
            data: [],
        }],
    },
    options: {
        showLines: true,
        title: {
            display: true,
            text: "Temperature",
        }
    }
});
