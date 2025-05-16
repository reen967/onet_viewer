const GITHUB_RAW = 'https://raw.githubusercontent.com/reen967/onet_data/main/';
const OCCUPATIONS_CSV = GITHUB_RAW + 'occupation_data.csv';
const ABILITIES_CSV = GITHUB_RAW + 'abilities.csv';

let occupations = [];
let abilities = [];

window.onload = () => {
  loadCSVs().then(() => {
    document.getElementById('searchBox').addEventListener('input', displayResults);
    displayResults();
  }).catch(err => {
    console.error('Error loading data:', err);
    document.getElementById('results').innerHTML = '<p>Error loading data.</p>';
  });
};

async function loadCSVs() {
  const occData = await fetchCSV(OCCUPATIONS_CSV);
  const abilData = await fetchCSV(ABILITIES_CSV);

  occupations = occData.filter(o => o['O*NET-SOC Code'] && o['Title']);
  abilities = abilData.filter(a => a['Scale ID'] === 'IM' && a['O*NET-SOC Code']);
}

function fetchCSV(url) {
  return fetch(url)
    .then(r => r.text())
    .then(t => Papa.parse(t, { header: true, skipEmptyLines: true }).data);
}

function displayResults() {
  const q = document.getElementById('searchBox').value.toLowerCase();
  const container = document.getElementById('results');
  container.innerHTML = '';

  const matches = occupations.filter(o => o['Title'].toLowerCase().includes(q)).slice(0, 10);

  for (const occ of matches) {
    const code = occ['O*NET-SOC Code'];
    const matched = abilities.filter(a => a['O*NET-SOC Code'] === code);
    const abilityList = matched.map(a =>
      `<li>${a['Abilities Element Name']} (Importance: ${a['Data Value']})</li>`).join('');

    container.innerHTML += `
      <div class="occupation">
        <h2>${occ['Title']}</h2>
        <p>${occ['Description']}</p>
        <strong>Abilities:</strong>
        <ul>${abilityList || '<li>No abilities listed</li>'}</ul>
      </div>
    `;
  }
}
