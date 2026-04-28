function sendData() {

    let x = document.getElementById("xdata").value.split(",").map(Number);
    let y = document.getElementById("ydata").value.split(",").map(Number);

    fetch("/fit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            x: x,
            y: y,
            model: document.getElementById("model").value
        })
    })
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }
    
        let resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = "";
    
        data.parameters.forEach(p => {
            resultsDiv.innerHTML += 
                `${p.name} = ${p.value.toFixed(5)} ± ${p.uncertainty.toFixed(5)}<br>`;
        });
    
        Plotly.newPlot("plot", data.graph.data, data.graph.layout || {});
    });
}