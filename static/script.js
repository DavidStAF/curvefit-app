function sendData() {

    let x = document.getElementById("xdata").value
            .split(/[\s,]+/)
            .map(v => parseFloat(v.trim()));

    let y = document.getElementById("ydata").value
            .split(/[\s,]+/)
            .map(v => parseFloat(v.trim()));
    console.log("X:", x);
    console.log("Y:", y);
    fetch("/fit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            x: x,
            y: y,
            model: document.getElementById("model").value,
            title: document.getElementById("title").value,
            xlabel: document.getElementById("xlabel").value,
            ylabel: document.getElementById("ylabel").value
        })
    })
    .then(response => response.json())
    .then(data => {
    
        if (data.error) {
            alert("Error: " + data.error);
            return;
        }
    
        // Affichage paramètres
        let resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = "";
    
        data.parameters.forEach(p => {
            resultsDiv.innerHTML += 
                `${p.name} = ${p.value.toFixed(5)} ± ${p.uncertainty.toFixed(5)}<br>`;
        });
    
        // 👇 IMPORTANT : utiliser data.graph directement
        Plotly.newPlot(
            "plot",
            data.graph.data,
            data.graph.layout
        );
    });
}