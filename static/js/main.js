import Autocomplete from "https://cdn.jsdelivr.net/gh/lekoala/bootstrap5-autocomplete@master/autocomplete.js";

// Cargar un animal en la tarjeta de información
function cargarAnimal(animal) {
  document.querySelector("#nombre").textContent = animal.name;
  document.querySelector("#descripcion").textContent = animal.description;
  document.querySelector("#imagen").src = `/static/img/galeria/${animal.id}.jpg`;
  document.querySelector("#imagen").alt = animal.name;
}

// Cargar los datos de los animales desde el archivo JSON
fetch("/static/data.json")
  .then((respuesta) => respuesta.json())
  .then((datos) => {
    // Cargar el primer animal al inicio
    // cargarAnimal(datos[0]);

    // Inicia el componente de autocompletado con los datos de los animales
    Autocomplete.init("input.autocomplete", {
      items: datos,
      valueField: "id",
      labelField: "name",
      highlightTyped: true,
      onSelectItem: (item) => {
        // Cada vez que se selecciona un elemento, se actualizan los campos de la tarjeta
        cargarAnimal(item);
      },
    });
  });
