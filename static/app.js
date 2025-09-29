const apiUrl = "http://127.0.0.1:5000/drivers/2021";

async function fetchDrivers() {
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error("Erreur réseau");

        const drivers = await response.json();
        const tbody = document.querySelector("#drivers-table tbody");
        tbody.innerHTML = "";

        drivers.forEach(driver => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${driver.familyName}</td>
                <td>${driver.givenName}</td>
                <td>${driver.code}</td>
                <td>${driver.nationality}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Erreur:", error);
    }
}

window.onload = fetchDrivers;
