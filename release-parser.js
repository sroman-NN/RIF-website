async function loadReleases() {
    try {
        const response = await fetch('manifest.json');
        const data = await response.json();
        const container = document.getElementById('list');
        
        data.releases.forEach((entry, index) => {
            const parts = entry.split('|').map(p => p.trim());
            if (parts.length < 3) return;

            const fileName = parts[0];
            const version = parts[1];
            const dateTime = parts[2];
            const devlogFile = parts[3]; 

            if (index > 0) {
                const hr = document.createElement('hr');
                container.appendChild(hr);
            }

            const item = document.createElement('div');
            item.className = 'release-item';
            
            let devlogLink = "";
            if (devlogFile) {
                devlogLink = `<a href="releases/${devlogFile}" style=" cursor: pointer; text-decoration: underline; margin-left: 10px;">VIEW-DEVLOG</a>`;
            }

            item.innerHTML = `
                <img src="file.png" alt="File Icon" onclick="window.location.href='releases/${fileName}.zip'">
                <div class="release-info">
                    <h3 onclick="window.location.href='releases/${fileName}.zip'">${fileName}</h3>
                    <div class="release-meta">
                        <strong onclick="window.location.href='releases/${fileName}.zip'">${version}</strong>
                        <span onclick="window.location.href='releases/${fileName}.zip'">${dateTime}</span>
                        ${devlogLink}
                    </div>
                </div>
            `;

            container.appendChild(item);
        });
    } catch (e) {
        console.error("Error loading manifest:", e);
    }
}
loadReleases();
