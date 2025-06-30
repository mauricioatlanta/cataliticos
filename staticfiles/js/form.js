document.addEventListener('DOMContentLoaded', function () {
    cargarRegiones();

    document.getElementById('agregar-fila').addEventListener('click', function () {
        const tabla = document.getElementById('tabla-cataliticos').querySelector('tbody');
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td><input type="text" name="codigo[]" class="codigo-input w-full bg-black text-white p-1 border rounded"></td>
            <td><input type="number" name="cantidad[]" value="1" class="cantidad-input w-full bg-black text-white p-1 border rounded"></td>
            <td><input type="number" name="valor_unitario[]" readonly class="valor-input w-full bg-black text-white p-1 border rounded"></td>
            <td><input type="number" name="subtotal[]" readonly class="subtotal-input w-full bg-black text-white p-1 border rounded"></td>
            <td><button type="button" class="eliminar-fila text-red-500 hover:underline">🗑️</button></td>
        `;
        tabla.appendChild(fila);
    });

    document.getElementById('tabla-cataliticos').addEventListener('click', function (e) {
        if (e.target.classList.contains('eliminar-fila')) {
            e.target.closest('tr').remove();
            actualizarTotal();
        }
    });

    document.getElementById('tabla-cataliticos').addEventListener('input', function (e) {
        const fila = e.target.closest('tr');
        const cantidad = parseFloat(fila.querySelector('.cantidad-input').value) || 0;
        const valor = parseFloat(fila.querySelector('.valor-input').value) || 0;
        fila.querySelector('.subtotal-input').value = (cantidad * valor).toFixed(0);
        actualizarTotal();
    });

    document.getElementById('tabla-cataliticos').addEventListener('blur', function (e) {
        if (e.target.classList.contains('codigo-input')) {
            const codigo = e.target.value.trim();
            const fila = e.target.closest('tr');
            if (codigo !== '') {
                fetch(`/api/catalitico/?term=${encodeURIComponent(codigo)}`)
                    .then(response => response.json())
                    .then(data => {
                        // Buscar el match por código exacto
                        const match = data.results.find(item =>
                            item.text.toLowerCase() === codigo.toLowerCase()
                        );
                        const valor = match ? match.valor : 0;
                        fila.querySelector('input[name="valor_unitario[]"]').value = valor;
                        const cantidad = parseFloat(fila.querySelector('input[name="cantidad[]"]').value) || 0;
                        fila.querySelector('input[name="subtotal[]"]').value = (cantidad * valor).toFixed(0);
                        actualizarTotal();
                    });
            }
        }
    }, true);
});

function actualizarTotal() {
    let total = 0;
    document.querySelectorAll('.subtotal-input').forEach(input => {
        total += parseFloat(input.value) || 0;
    });
    document.getElementById('total_general').textContent = total.toLocaleString('es-CL');
}

function cargarRegiones() {
    fetch('/static/js/regiones_ciudades.json')
        .then(response => response.json())
        .then(data => {
            const regionSelect = document.getElementById('region');
            const ciudadSelect = document.getElementById('ciudad');
            regionSelect.innerHTML = '<option value="">Selecciona región</option>';
            ciudadSelect.innerHTML = '<option value="">Selecciona ciudad</option>';
            for (const region in data) {
                regionSelect.innerHTML += `<option value="${region}">${region}</option>`;
            }
            regionSelect.addEventListener('change', function () {
                const ciudades = data[this.value] || [];
                ciudadSelect.innerHTML = '<option value="">Selecciona ciudad</option>';
                ciudades.forEach(ciudad => {
                    ciudadSelect.innerHTML += `<option value="${ciudad}">${ciudad}</option>`;
                });
            });
        });
}
