function acceptMatch(externalId, internalId) {
  const payload = { external_id: externalId, internal_id: internalId };
  
  fetch('/accept', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).then(res => {
    if (res.ok) {
      removeMatchCard(externalId, internalId);
    } else {
      console.error("Failed to record match, status:", res.status);
      alert("Failed to record match.");
    }
  }).catch(error => {
    console.error("Error accepting match:", error);
    alert("Error recording match.");
  });
}

function removeMatchCard(externalId, internalId) {
  // Use the exact card ID format from your template
  const cardId = `match-card-${externalId}-${internalId}`;
  const card = document.getElementById(cardId);
  
  if (card) {
    card.classList.add('fade-out');
    setTimeout(() => card.remove(), 500);
  } else {
    console.warn("Could not find card to remove:", cardId);
  }
}
