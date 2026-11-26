const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
const roomForm = document.getElementById('suiteForm');
const facilityForm = document.getElementById('facForm');

function updateRoomEstimate() {
    const { check_in, check_out, room_id, extension_hours } = roomForm.elements;
    const rate = Number(room_id.selectedOptions[0]?.dataset.rate);
    const nights = (Date.parse(check_out.value) - Date.parse(check_in.value)) / 86400000;
    const surcharge = Number(extension_hours.value) > 2 ? Number(roomForm.dataset.extension) : 0;
    document.getElementById('computedDays').textContent = nights > 0 ? nights + (nights === 1 ? ' night' : ' nights') : '—';
    document.getElementById('computedCost').textContent = nights > 0 && Number.isFinite(rate) ? usd.format(nights * rate + surcharge) : '—';
}

function updateFacilityEstimate() {
    const { facility_id, duration_hours, is_eating } = facilityForm.elements;
    const rate = Number(facility_id.selectedOptions[0]?.dataset.rate);
    const hours = Number(duration_hours.value);
    const multiplier = is_eating.value === '1' ? 1 - Number(facilityForm.dataset.discount) : 1;
    document.getElementById('computedFacCost').textContent = hours >= 1 && hours <= 8 && Number.isFinite(rate)
        ? usd.format(rate * hours * multiplier)
        : '—';
}

roomForm.addEventListener('input', updateRoomEstimate);
facilityForm.addEventListener('input', updateFacilityEstimate);
updateRoomEstimate();
updateFacilityEstimate();

document.getElementById('open-payment')?.addEventListener('click', () => document.getElementById('cardModal').showModal());
