let currentMediaIndex = -1;
let currentMediaArray = [];

async function readRoute(route) {
    try {
        const response = await fetch(route);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Failed to fetch data from ${route}:`, error);
        return null;
    }
}

async function generateVideoThumbnail(file) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        video.src = URL.createObjectURL(file);
        
        video.addEventListener('loadedmetadata', () => {
            video.currentTime = 5;
        });

        video.addEventListener('seeked', () => {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const thumbnail = canvas.toDataURL('image/jpeg');
            URL.revokeObjectURL(video.src);
            resolve(thumbnail);
        });

        video.addEventListener('error', (e) => {
            reject(e);
        });

        video.addEventListener('seeked', () => {
            video.pause();
        });
    });
}

async function getThumbnail(path) {
    const extension = path.split('.').pop().toLowerCase();
    if (['mp4', 'webm', 'ogg'].includes(extension)) {
        try {
            const response = await fetch(`/media${path}`);
            const blob = await response.blob();
            const thumbnail = await generateVideoThumbnail(blob);
            return thumbnail;
        } catch (error) {
            console.error('Failed to generate video thumbnail:', error);
            return '/path/to/default/thumbnail.jpg';
        }
    } else {
        return `/media${path}`;
    }
}

async function displayData(route) {
    const data = await readRoute(route);
    if (data === null) {
        const container = document.getElementById('dataContainer');
        if (container) {
            container.textContent = 'Failed to fetch data.';
        }
        return;
    }

    const container = document.getElementById('dataContainer');
    if (container) {
        container.innerHTML = '';

        for (const [groupName, paths] of data) {
            const pathsArray = paths.split(',');
            const firstMediaPath = pathsArray[0].trim();
            const thumbnail = await getThumbnail(firstMediaPath);

            const groupCard = document.createElement('div');
            groupCard.className = 'card group';
            groupCard.innerHTML = `
                <img src="${thumbnail}" alt="${groupName}" class="thumbnail">
                <div class="group-name">${groupName}</div>
            `;
            groupCard.addEventListener('click', () => displayGroup(groupName, pathsArray));
            container.appendChild(groupCard);
        }
    } else {
        console.error('Container element not found');
    }
}

async function displayGroup(groupName, pathsArray) {
    const container = document.getElementById('dataContainer');
    if (container) {
        container.innerHTML = '';

        for (const path of pathsArray) {
            const trimmedPath = path.trim();
            const thumbnail = await getThumbnail(trimmedPath);

            const mediaCard = document.createElement('div');
            mediaCard.className = 'card';
            mediaCard.innerHTML = `
                <img src="${thumbnail}" alt="${groupName}" class="thumbnail">
            `;
            mediaCard.addEventListener('click', () => openMedia(pathsArray, pathsArray.indexOf(trimmedPath)));
            container.appendChild(mediaCard);
        }
    } else {
        console.error('Container element not found');
    }
}

function openMedia(mediaArray, mediaIndex) {
    currentMediaArray = mediaArray;
    currentMediaIndex = mediaIndex;

    const mediaUrl = `/media${currentMediaArray[currentMediaIndex]}`;
    const mediaExtension = currentMediaArray[currentMediaIndex].split('.').pop().toLowerCase();
    const mediaContent = document.getElementById('mediaContent');
    const floatingWindow = document.getElementById('floatingWindow');

    if (['mp4', 'webm', 'ogg'].includes(mediaExtension)) {
        mediaContent.innerHTML = `<video src="${mediaUrl}" controls autoplay style="max-width: 100%; max-height: 100%;"></video>`;
    } else {
        mediaContent.innerHTML = `<img src="${mediaUrl}" alt="Media" style="max-width: 100%; max-height: 100%;">`;
    }

    floatingWindow.style.display = 'block';
}

function closeMedia() {
    const floatingWindow = document.getElementById('floatingWindow');
    floatingWindow.style.display = 'none';
    document.getElementById('mediaContent').innerHTML = '';
}

function prevMedia() {
    if (currentMediaIndex > 0) {
        openMedia(currentMediaArray, currentMediaIndex - 1);
    }
}

function nextMedia() {
    if (currentMediaIndex < currentMediaArray.length - 1) {
        openMedia(currentMediaArray, currentMediaIndex + 1);
    }
}
