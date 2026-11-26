function coupleDates(arrival, departure) {
    if (!arrival || !departure) return;
    const update = () => {
        const next = new Date(arrival.value + "T00:00:00Z");
        if (Number.isNaN(next.getTime())) return;
        next.setUTCDate(next.getUTCDate() + 1);
        const minimum = next.toISOString().slice(0, 10);
        departure.min = minimum;
        if (!departure.value || departure.value < minimum) departure.value = minimum;
    };
    arrival.addEventListener("input", update);
    update();
}

coupleDates(document.getElementById("arrive"), document.getElementById("depart"));
coupleDates(document.getElementById("checkInDate"), document.getElementById("checkOutDate"));

const signInMenu = document.querySelector(".sign-in-menu");
if (signInMenu) {
    document.addEventListener("pointerdown", event => {
        if (!signInMenu.contains(event.target)) signInMenu.open = false;
    });
    signInMenu.addEventListener("keydown", event => {
        if (event.key !== "Escape" || !signInMenu.open) return;
        signInMenu.open = false;
        signInMenu.querySelector("summary").focus();
    });
}
