let autocomplete;

function initAutocomplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById("location"), {
            componentRestrictions: {
                "country": ["IE"]
            },
            fields: ["place_id", "geometry", "name"]
        });
    autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
    var place = autocomplete.getPlace();

    if (!place.geometry) {
        // User did not select a prediction; reset the input field
        document.getElementById("location").placeholder = "Enter a Place";
    }
}