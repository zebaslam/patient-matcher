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
  const cardId = `match-card-${externalId}-${internalId}`;
  const card = document.getElementById(cardId);

  if (card) {
    card.classList.add('fade-out');
    setTimeout(() => {
      card.remove();
      decrementMatchesCounter(); // Decrement after removing the card
    }, 500);
  } else {
    console.warn("Could not find card to remove:", cardId);
  }
}

function decrementMatchesCounter() {
  const counter = document.getElementById('matches-counter');
  if (counter) {
    let count = parseInt(counter.textContent, 10);
    if (count > 0) {
      counter.textContent = count - 1;
    }
  }
}

// Initialize all Bootstrap tooltips on page load
document.addEventListener('DOMContentLoaded', function () {
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

function copyPatientJson(patientObj, label) {
  const jsonStr = JSON.stringify(patientObj, null, 2);
  if (navigator.clipboard) {
    navigator.clipboard.writeText(jsonStr).then(() => {
      alert(`${label} JSON copied to clipboard!`);
    }, () => {
      alert('Failed to copy JSON.');
    });
  } else {
    // Fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = jsonStr;
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      alert(`${label} JSON copied to clipboard!`);
    } catch (err) {
      alert('Failed to copy JSON.');
    }
    document.body.removeChild(textarea);
  }
}

function copyPatientJsonFromButton(btn, label) {
  const patientObj = JSON.parse(btn.getAttribute('data-patient'));
  copyPatientJson(patientObj, label);
}
