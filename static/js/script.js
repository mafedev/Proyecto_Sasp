// Script para Empresa
const formEmpresa = document.getElementById('formEmpresa');
const resultadoEmpresa = document.getElementById('resultadoEmpresa');

if (formEmpresa) {
    formEmpresa.addEventListener('submit', function (e) {
        e.preventDefault();

        const empleados = parseFloat(document.getElementById('empleados').value);
        const electricidad = parseFloat(document.getElementById('electricidadEmpresa').value);
        const vehiculos = parseFloat(document.getElementById('vehiculos').value);
        const kmVehiculos = parseFloat(document.getElementById('kmVehiculos').value);
        const vuelos = parseFloat(document.getElementById('vuelosEmpresa').value);
        const residuos = parseFloat(document.getElementById('residuos').value);
        const papel = parseFloat(document.getElementById('papel').value);

        const CO2_electricidad = electricidad * 12 * 0.4;
        const CO2_vehiculos = vehiculos * kmVehiculos * 12 * 0.21;
        const CO2_vuelos = vuelos * 250;
        const CO2_residuos = residuos * 12 * 1.8;
        const CO2_papel = papel * 12 * 6;

        const total = CO2_electricidad + CO2_vehiculos + CO2_vuelos + CO2_residuos + CO2_papel;
        const totalPerCapita = total / empleados;

        resultadoEmpresa.style.display = 'block';
        resultadoEmpresa.innerHTML = `
            <h2>Resultado empresarial 🌍</h2>
            <p><strong>Emisiones totales: ${total.toFixed(2)} kg CO₂/año</strong></p>
            <p><strong>Emisiones por empleado: ${totalPerCapita.toFixed(2)} kg CO₂/año</strong></p>
            <p>${totalPerCapita > 4000 ? '¡Hay margen de mejora! 🌱' : '¡Buen trabajo, sigan así! ✅'}</p>
        `;
    });
}

// Script para Persona
const form = document.getElementById('formHuella');
const resultado = document.getElementById('resultado');

if (form) {
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const km = parseFloat(document.getElementById('km').value);
        const carne = parseFloat(document.getElementById('carne').value);
        const electricidad = parseFloat(document.getElementById('electricidad').value);
        const vuelos = parseFloat(document.getElementById('vuelos').value);

        const CO2_coche = km * 52 * 0.21;
        const CO2_carne = carne * 52 * 7;
        const CO2_elec = electricidad * 12 * 0.4;
        const CO2_vuelos = vuelos * 250;

        const total = CO2_coche + CO2_carne + CO2_elec + CO2_vuelos;

        resultado.style.display = 'block';
        resultado.innerHTML = `
            <h2>Tu huella anual estimada es de:</h2>
            <p><strong>${total.toFixed(2)} kg de CO₂</strong></p>
            <p>🌍 Promedio mundial: 4000 kg CO₂/año por persona.</p>
            <p>${total > 4000 ? '¡Puedes mejorar! 🌱' : '¡Estás por debajo del promedio, bien hecho! ✅'}</p>
        `;
    });
}
