function acceptMatch(externalId, internalId) {
  fetch('/accept', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ external_id: externalId, internal_id: internalId })
  }).then(res => {
    if (res.ok) {
       console.log("Sending:", { external_id: externalId, internal_id: internalId });
      removeMatchCard(externalId, internalId);
    } else {
      alert("Failed to record match.");
    }
  });
}

function removeMatchCard(externalId, internalId) {
  const cardId = `match-card-${externalId}-${internalId}`;
  const card = document.getElementById(cardId);
  if (card) {
    card.classList.add('fade-out');
    setTimeout(() => card.remove(), 500);  // match transition duration
  }
}

